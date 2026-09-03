import { get, list, put } from "@vercel/blob";

const STORE_PATH = "pkl/submissions.json";
const APPLICATIONS_PATH = "pkl/reviewer-applications.json";

function blobOptions() {
  const storeId = process.env.BLOB_STORE_ID;
  const legacyToken = process.env.BLOB_READ_WRITE_TOKEN;

  if (legacyToken) return { token: legacyToken };
  if (storeId) return { storeId };
  throw new Error("submission storage is not configured");
}

async function readJson(path, fallback) {
  const options = blobOptions();
  const { blobs } = await list({ prefix: path, limit: 10, ...options });
  const blob = blobs.find((item) => item.pathname === path);
  if (!blob) return fallback;

  const result = await get(blob.url, { access: "private", ...options });
  if (!result?.stream) throw new Error("submission store unavailable");

  const text = await new Response(result.stream).text();
  return JSON.parse(text);
}

async function writeJson(path, value) {
  const options = blobOptions();
  await put(path, JSON.stringify(value, null, 2), {
    access: "private",
    addRandomSuffix: false,
    allowOverwrite: true,
    contentType: "application/json",
    ...options,
  });
}

const readStore = () => readJson(STORE_PATH, { submissions: [], audit: [] });
const writeStore = (store) => writeJson(STORE_PATH, store);
const readApplications = () => readJson(APPLICATIONS_PATH, { applications: [] });
const writeApplications = (store) => writeJson(APPLICATIONS_PATH, store);

function normalise(value) {
  return String(value ?? "").trim().toLowerCase().replace(/\s+/g, " ");
}

function fingerprint(item) {
  return [item.title, item.statement, item.category].map(normalise).join("\n");
}

function validate(item) {
  if (!normalise(item.title) || !normalise(item.statement) || !normalise(item.category)) return "title, statement, and category are required";
  if (String(item.title).trim().length > 240) return "title is too long";
  if (String(item.statement).trim().length > 10000) return "statement is too long";
  if (String(item.category).trim().length > 120) return "category is too long";
  return null;
}

export function validateReviewerApplication(item) {
  if (!item || typeof item !== "object") return "application details are required";
  const required = ["name", "email", "background", "subject_areas", "motivation", "availability", "conflicts"];
  if (required.some((field) => !String(item[field] ?? "").trim())) return "please complete every application field";
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(item.email).trim())) return "please enter a valid email address";
  if (item.consent !== true) return "please confirm the privacy notice";
  const limits = { name: 120, email: 254, background: 2000, subject_areas: 1000, motivation: 3000, availability: 1000, conflicts: 2000 };
  for (const [field, limit] of Object.entries(limits)) {
    if (String(item[field]).trim().length > limit) return `${field.replaceAll("_", " ")} is too long`;
  }
  return null;
}

function parseBody(req) {
  if (req.body && typeof req.body === "object") return req.body;
  try {
    return JSON.parse(req.body || "{}");
  } catch {
    return null;
  }
}

export function publicProjection(item) {
  const {
    contributor_id: _contributorId,
    rate_limit_id: _rateLimitId,
    review_note: _reviewNote,
    ...publicItem
  } = item;
  return publicItem;
}

function json(res, status, body) {
  res.statusCode = status;
  res.setHeader("Content-Type", "application/json");
  res.setHeader("Cache-Control", "no-store");
  res.setHeader("X-Content-Type-Options", "nosniff");
  res.end(JSON.stringify(body));
}

export default async function handler(req, res) {
  const path = new URL(req.url, "https://pkl.local").pathname;

  if (req.method === "GET" && path === "/api/health") {
    try {
      const store = await readStore();
      return json(res, 200, {
        status: "ok",
        storage: "available",
        submissions: store.submissions.length,
        api_version: "v1",
      });
    } catch (error) {
      console.error("submission API health check failed", error);
      return json(res, 503, { status: "degraded", storage: "unavailable", code: "storage_read" });
    }
  }

  try {
    if (path.startsWith("/api/reviewer/")) {
      const configuredToken = process.env.PKL_REVIEWER_TOKEN;
      const supplied = (req.headers.authorization || "").replace(/^Bearer\s+/i, "");
      if (!configuredToken) return json(res, 503, { error: "reviewer API is not configured", code: "reviewer_unconfigured" });
      if (supplied !== configuredToken) return json(res, 401, { error: "reviewer authentication required", code: "unauthorized" });
    }

    if (req.method === "POST" && path === "/api/reviewer-applications") {
      const body = parseBody(req);
      if (!body) return json(res, 400, { error: "request body must be valid JSON", code: "invalid_json" });
      const validationError = validateReviewerApplication(body);
      if (validationError) return json(res, 400, { error: validationError, code: "validation" });

      let applications;
      try {
        applications = await readApplications();
      } catch (error) {
        console.error("reviewer application storage read failed", error);
        return json(res, 503, { error: "application storage is temporarily unavailable", code: "application_storage_read" });
      }

      const contributorId = req.headers["x-contributor-id"] || "anonymous";
      const now = new Date();
      const cutoff = now.getTime() - 3600000;
      const recent = applications.applications.filter((item) => item.rate_limit_id === contributorId && Date.parse(item.created_at) >= cutoff);
      if (recent.length >= 3) return json(res, 429, { error: "application rate limit exceeded", code: "rate_limit" });

      const application = {
        id: `PKL-REVAPP-${crypto.randomUUID().replaceAll("-", "").slice(0, 12)}`,
        name: String(body.name).trim(),
        email: String(body.email).trim(),
        background: String(body.background).trim(),
        subject_areas: String(body.subject_areas).trim(),
        motivation: String(body.motivation).trim(),
        availability: String(body.availability).trim(),
        conflicts: String(body.conflicts).trim(),
        rate_limit_id: contributorId,
        status: "pending",
        created_at: now.toISOString(),
      };
      applications.applications.push(application);
      try {
        await writeApplications(applications);
      } catch (error) {
        console.error("reviewer application storage write failed", error);
        return json(res, 503, { error: "application could not be saved", code: "application_storage_write" });
      }
      return json(res, 201, { application: { id: application.id, status: application.status, created_at: application.created_at } });
    }

    if (req.method === "GET" && path === "/api/reviewer/applications") {
      try {
        const applications = await readApplications();
        return json(res, 200, { applications: applications.applications.map(({ rate_limit_id: _rateLimitId, ...application }) => application) });
      } catch (error) {
        console.error("reviewer application storage read failed", error);
        return json(res, 503, { error: "application storage is temporarily unavailable", code: "application_storage_read" });
      }
    }

    let submissionBody = null;
    if (req.method === "POST" && path === "/api/submissions") {
      submissionBody = parseBody(req);
      if (!submissionBody) return json(res, 400, { error: "request body must be valid JSON", code: "invalid_json" });
      const error = validate(submissionBody);
      if (error) return json(res, 400, { error, code: "validation" });
    }

    const store = await readStore();

    if (req.method === "GET" && path === "/api/public/submissions") {
      return json(res, 200, { submissions: store.submissions.filter((item) => item.status === "accepted").map(publicProjection) });
    }

    if (req.method === "GET" && path === "/api/v1/claims") {
      return json(res, 200, {
        data: store.submissions.filter((item) => item.status === "accepted").map(publicProjection),
        meta: { api_version: "v1", count: store.submissions.filter((item) => item.status === "accepted").length },
      });
    }

    if (req.method === "POST" && path === "/api/submissions") {
      const body = submissionBody;

      const contributorId = req.headers["x-contributor-id"] || null;
      const limiter = contributorId || "anonymous";
      const now = new Date();
      const cutoff = now.getTime() - 3600000;
      const recent = store.submissions.filter((item) => (item.rate_limit_id || item.contributor_id || "anonymous") === limiter && Date.parse(item.created_at) >= cutoff);
      if (recent.length >= 5) return json(res, 429, { error: "submission rate limit exceeded", code: "rate_limit" });

      const candidate = {
        id: `PKL-SUB-${crypto.randomUUID().replaceAll("-", "").slice(0, 12)}`,
        title: String(body.title).trim(),
        statement: String(body.statement).trim(),
        category: String(body.category).trim(),
        evidence: Array.isArray(body.evidence) ? body.evidence.map(String).map((x) => x.trim()).filter(Boolean) : [],
        limitations: Array.isArray(body.limitations) ? body.limitations.map(String).map((x) => x.trim()).filter(Boolean) : [],
        relationships: Array.isArray(body.relationships) ? body.relationships.map(String).map((x) => x.trim()).filter(Boolean) : [],
        contributor_id: contributorId,
        rate_limit_id: limiter,
        status: "pending_review",
        created_at: now.toISOString(),
        reviewed_at: null,
        review_note: null,
      };

      if (store.submissions.some((item) => fingerprint(item) === fingerprint(candidate))) {
        return json(res, 409, { error: "duplicate submission", code: "duplicate" });
      }

      store.submissions.push(candidate);
      store.audit.push({ action: "submitted", submission_id: candidate.id, at: candidate.created_at });
      try {
        await writeStore(store);
      } catch (error) {
        console.error("submission write failed", error);
        return json(res, 503, { error: "submission storage write failed", code: "storage_write" });
      }
      return json(res, 201, { submission: candidate });
    }

    if (path.startsWith("/api/reviewer/")) {
      if (req.method === "GET" && path === "/api/reviewer/submissions") {
        return json(res, 200, { submissions: store.submissions.filter((item) => item.status === "pending_review") });
      }
      if (req.method === "GET" && path === "/api/reviewer/audit") return json(res, 200, { audit: store.audit });

      const match = path.match(/^\/api\/reviewer\/submissions\/([^/]+)\/decision$/);
      if (req.method === "POST" && match) {
        const body = parseBody(req);
        if (!body) return json(res, 400, { error: "request body must be valid JSON", code: "invalid_json" });
        const item = store.submissions.find((entry) => entry.id === decodeURIComponent(match[1]));
        if (!item) return json(res, 404, { error: "submission not found", code: "not_found" });
        if (item.status !== "pending_review") return json(res, 409, { error: "only pending submissions can be moderated", code: "invalid_transition" });
        if (!["accepted", "rejected"].includes(body.status) || !String(body.reviewer_id || "").trim()) return json(res, 400, { error: "invalid moderation request", code: "validation" });
        item.status = body.status;
        item.reviewed_at = new Date().toISOString();
        item.review_note = String(body.note || "").trim() || null;
        store.audit.push({ action: item.status, submission_id: item.id, reviewer_id: String(body.reviewer_id), at: item.reviewed_at });
        try {
          await writeStore(store);
        } catch (error) {
          console.error("moderation write failed", error);
          return json(res, 503, { error: "submission storage write failed", code: "storage_write" });
        }
        return json(res, 200, { submission: item });
      }
    }

    return json(res, 404, { error: "not found" });
  } catch (error) {
    console.error("submission API read failed", error);
    return json(res, 503, { error: "submission storage read failed", code: "storage_read" });
  }
}
