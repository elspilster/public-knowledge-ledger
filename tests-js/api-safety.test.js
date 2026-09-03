import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

import { publicProjection } from "../api/index.js";

test("public projection removes contributor and moderation-only fields", () => {
  const projected = publicProjection({
    id: "PKL-SUB-1",
    title: "Visible",
    status: "accepted",
    contributor_id: "private-contributor",
    rate_limit_id: "private-rate-limit",
    review_note: "internal note",
    reviewed_at: "2026-09-03T00:00:00Z",
  });

  assert.deepEqual(projected, {
    id: "PKL-SUB-1",
    title: "Visible",
    status: "accepted",
    reviewed_at: "2026-09-03T00:00:00Z",
  });
});

test("deployed frontend entrypoint delegates to the canonical handler", async () => {
  const source = await readFile(new URL("../frontend/api/index.js", import.meta.url), "utf8");
  assert.match(source, /export \{ default \} from "\.\.\/\.\.\/api\/index\.js"/);
  assert.doesNotMatch(source, /BLOB_READ_WRITE_TOKEN|access:\s*"public"/);
});

test("versioned and health endpoints have Vercel route files", async () => {
  const paths = [
    "../api/health.js",
    "../api/v1/claims.js",
    "../frontend/api/health.js",
    "../frontend/api/v1/claims.js",
  ];
  for (const path of paths) {
    const source = await readFile(new URL(path, import.meta.url), "utf8");
    assert.match(source, /export \{ default \} from/);
  }
});
