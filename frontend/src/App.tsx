import { useEffect, useMemo, useState } from "react";
import { ClaimRecord } from "./pages/ClaimRecord";
import type { Claim } from "./types/claim";
import "./App.css";

const API_BASE = (import.meta.env.VITE_PKL_API_URL || "/api").replace(/\/$/, "");

const seedClaims: Claim[] = [
  {
    id: "PKL-BIO-001",
    title: "DNA encodes hereditary genetic information",
    statement: "DNA contains the biological information used to store and transmit hereditary information in living organisms.",
    category: "Molecular Biology",
    status: "Established",
    evidence: ["Experimental evidence from molecular genetics", "DNA structure research and sequencing evidence", "Functional evidence linking genes to inherited traits"],
    limitations: ["DNA is not the only factor influencing biological traits", "Gene regulation affects how information is expressed", "Biological systems involve complex interactions"],
    relationships: ["Evolution", "Genetic variation", "Epigenetics"],
  },
  {
    id: "PKL-PHY-001",
    title: "Objects near Earth's surface accelerate downward",
    statement: "In the absence of significant air resistance, objects near Earth's surface experience approximately uniform downward gravitational acceleration.",
    category: "Physics",
    status: "Established",
    evidence: ["Repeated experimental measurements of gravitational acceleration", "Classical mechanics and modern gravitational theory"],
    limitations: ["The approximation varies with altitude and location", "Air resistance changes the motion of many real objects"],
    relationships: ["Gravity", "Classical mechanics", "General relativity"],
  },
  {
    id: "PKL-EAR-001",
    title: "Earth's climate has changed throughout geological history",
    statement: "Earth's climate has varied substantially over geological time as a result of interacting physical, chemical, biological, and astronomical factors.",
    category: "Earth Science",
    status: "Established",
    evidence: ["Ice-core, sediment, fossil, and isotope records", "Multiple independent paleoclimate reconstructions"],
    limitations: ["Past climate records have different resolutions and uncertainties", "The causes and timing of individual climate transitions can remain disputed"],
    relationships: ["Paleoclimate", "Carbon cycle", "Atmospheric composition"],
  },
];

type Submission = Claim & {
  contributor_id?: string | null;
  reviewed_at?: string | null;
  review_note?: string | null;
};

async function apiRequest<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
  });
  const body = await response.json().catch(() => ({ error: "Invalid API response" }));
  if (!response.ok) throw new Error(body.error || `Request failed (${response.status})`);
  return body as T;
}

function splitLines(value: string) {
  return value.split("\n").map((item) => item.trim()).filter(Boolean);
}

function Home({ onBrowse, onSubmit, onReviewer }: { onBrowse: () => void; onSubmit: () => void; onReviewer: () => void }) {
  return <><header className="home-nav"><button className="brand-link" type="button" aria-label="Public Knowledge Ledger home">PKL</button><nav aria-label="Primary navigation"><button className="nav-link" onClick={onBrowse} type="button">Browse ledger</button><a className="nav-help-link" href="/docs/PKL_User_Help_Guide_v1.0.pdf" target="_blank" rel="noreferrer">Help Guide</a><button className="nav-reviewer-link" onClick={onReviewer} type="button">Become a reviewer</button></nav></header><main className="landing-page">
    <section className="hero">
      <p className="eyebrow">PUBLIC KNOWLEDGE LEDGER</p>
      <h1>Knowledge should<br /><span>be traceable.</span></h1>
      <p className="hero-text">A public ledger for recording claims, evidence, limitations, relationships, and the current state of knowledge.</p>
      <div className="hero-actions">
        <button className="primary-button" onClick={onBrowse}>Browse the ledger</button>
        <button className="secondary-button" onClick={onSubmit} type="button">Submit a claim</button>
        <button className="secondary-button" onClick={onReviewer} type="button">Become a reviewer</button>
      </div>
    </section>
    <section className="principles">
      <article><h2>Claims</h2><p>Clear statements of what is being claimed.</p></article>
      <article><h2>Evidence</h2><p>A visible trail showing what supports a claim.</p></article>
      <article><h2>Uncertainty</h2><p>Limitations and unanswered questions remain part of the record.</p></article>
    </section>
    <section className="about-ledger"><p className="eyebrow">THE LEDGER</p><h2>Knowledge is allowed to change.</h2><p>PKL records are evidence assessments at a particular point in time. New evidence can strengthen, weaken, revise, or overturn an assessment.</p><div className="resource-links"><a href="/docs/PKL_User_Help_Guide_v1.0.pdf" target="_blank" rel="noreferrer">Read the Help Guide</a><a href="/docs/PKL_User_Help_Guide_v1.0.docx" download>Download Word edition</a></div></section>
  </main></>;
}

function Browse({ claims, onSelect, onBack }: { claims: Claim[]; onSelect: (claim: Claim) => void; onBack: () => void }) {
  const [query, setQuery] = useState("");
  const filtered = useMemo(() => {
    const value = query.trim().toLowerCase();
    return value ? claims.filter((claim) => [claim.id, claim.title, claim.category, claim.statement].join(" ").toLowerCase().includes(value)) : claims;
  }, [claims, query]);

  return <main className="browse-page">
    <section className="browse-header"><p className="eyebrow">THE LEDGER</p><h1>Browse knowledge records.</h1><input aria-label="Search claims" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search by title, category, ID, or text…" /></section>
    <section className="claim-list">
      {filtered.map((claim) => <button className="claim-card" key={claim.id} onClick={() => onSelect(claim)} type="button"><p>{claim.id}</p><h2>{claim.title}</h2><p>{claim.category}</p><strong>{claim.status}</strong><p>{claim.statement}</p></button>)}
      {filtered.length === 0 && <p>No matching records found.</p>}
    </section>
    <button className="secondary-button" onClick={onBack} type="button">Back to home</button>
  </main>;
}

function ClaimForm({ onCancel, onSubmitted }: { onCancel: () => void; onSubmitted: (message: string) => void }) {
  const [title, setTitle] = useState("");
  const [statement, setStatement] = useState("");
  const [category, setCategory] = useState("");
  const [evidence, setEvidence] = useState("");
  const [limitations, setLimitations] = useState("");
  const [relationships, setRelationships] = useState("");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true); setError("");
    try {
      await apiRequest("/submissions", {
        method: "POST",
        headers: { "X-Contributor-ID": `browser-${crypto.randomUUID()}` },
        body: JSON.stringify({ title, statement, category, evidence: splitLines(evidence), limitations: splitLines(limitations), relationships: splitLines(relationships) }),
      });
      onSubmitted("Submitted for review. It will not appear publicly until a reviewer accepts it.");
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Submission failed.");
    } finally { setSaving(false); }
  }

  return <main className="claim-form-page"><section className="claim-form-card"><p className="eyebrow">SUBMIT A CLAIM</p><h1>Propose a knowledge record.</h1><p className="form-intro">Submissions enter review and are not published directly to the public ledger.</p>
    <form onSubmit={submit}>
      <label>Claim title<input value={title} onChange={(event) => setTitle(event.target.value)} required /></label>
      <label>Statement<textarea value={statement} onChange={(event) => setStatement(event.target.value)} rows={5} required /></label>
      <label>Category<input value={category} onChange={(event) => setCategory(event.target.value)} required /></label>
      <label>Evidence<textarea value={evidence} onChange={(event) => setEvidence(event.target.value)} rows={5} placeholder="One item per line" /></label>
      <label>Known limitations<textarea value={limitations} onChange={(event) => setLimitations(event.target.value)} rows={5} placeholder="One item per line" /></label>
      <label>Related knowledge<textarea value={relationships} onChange={(event) => setRelationships(event.target.value)} rows={4} placeholder="One item per line" /></label>
      {error && <p className="error-message" role="alert">{error}</p>}
      <div className="form-actions"><button className="secondary-button" onClick={onCancel} type="button">Cancel</button><button className="primary-button" disabled={saving} type="submit">{saving ? "Submitting…" : "Submit for review"}</button></div>
    </form>
  </section></main>;
}


function ReviewerRecruitment({ onBack, onConsole }: { onBack: () => void; onConsole: () => void }) {
  const applyUrl = "https://github.com/elspilster/public-knowledge-ledger/issues/new?title=Reviewer%20application%20-%20%5Bname%5D&body=Name%20or%20pseudonym%3A%0ARelevant%20experience%3A%0ASubject%20areas%3A%0AWhy%20I%20want%20to%20review%20for%20PKL%3A%0APotential%20conflicts%20of%20interest%3A%0AApproximate%20availability%3A";
  return <main className="reviewers-page">
    <section className="reviewers-hero">
      <p className="eyebrow">FOUNDING REVIEWER OPPORTUNITY</p>
      <h1>Help make public knowledge more accountable.</h1>
      <p className="reviewers-lead">PKL is looking for thoughtful, independent people to assess submitted claims, examine evidence, record uncertainty, and help build a transparent public review process.</p>
      <div className="hero-actions"><a className="primary-button button-link" href={applyUrl} target="_blank" rel="noreferrer">Apply to become a reviewer</a><button className="secondary-button" onClick={onBack} type="button">Explore PKL first</button></div>
      <p className="opportunity-note">Founding-stage volunteer opportunity. Any future paid roles will be advertised transparently.</p>
    </section>
    <section className="reviewer-details">
      <article><p className="detail-number">01</p><h2>What you’ll do</h2><ul><li>Read claims and examine their cited evidence.</li><li>Check provenance, limitations, contradictions, and uncertainty.</li><li>Record clear reasons for accepting, returning, or rejecting submissions.</li><li>Declare relevant interests and step aside where independence is compromised.</li></ul></article>
      <article><p className="detail-number">02</p><h2>Who we’re looking for</h2><ul><li>Careful thinkers from academic, professional, technical, journalistic, or lived-experience backgrounds.</li><li>People comfortable saying “uncertain” when evidence is incomplete.</li><li>Reviewers willing to work to a published process and leave an auditable trail.</li><li>No formal qualification is mandatory; sound judgement and honesty matter.</li></ul></article>
      <article><p className="detail-number">03</p><h2>How trust is protected</h2><ul><li>Reviewer identity or an accountable public pseudonym is recorded.</li><li>Conflicts of interest must be disclosed.</li><li>Decisions require written reasons and remain open to later challenge.</li><li>Reviewers assess the evidence currently recorded, not whether a claim is eternally true.</li></ul></article>
    </section>
    <section className="reviewer-cta"><div><p className="eyebrow">EARLY TEAM</p><h2>Shape the review system with us.</h2><p>Founding reviewers will help test the process, improve the guidance, and establish a culture of independence, fairness, and transparent disagreement.</p></div><a className="primary-button button-link" href={applyUrl} target="_blank" rel="noreferrer">Start your application</a></section>
    <section className="existing-reviewer"><p>Already approved as a PKL reviewer?</p><button className="text-button" onClick={onConsole} type="button">Open the secure reviewer console →</button></section>
  </main>;
}

function Reviewer({ onBack }: { onBack: () => void }) {
  const [token, setToken] = useState(() => sessionStorage.getItem("pkl_reviewer_token") || "");
  const [reviewerId, setReviewerId] = useState(() => sessionStorage.getItem("pkl_reviewer_id") || "");
  const [queue, setQueue] = useState<Submission[]>([]);
  const [audit, setAudit] = useState<Array<Record<string, string>>>([]);
  const [error, setError] = useState("");
  const [ready, setReady] = useState(false);

  async function load() {
    setError("");
    try {
      const headers = { Authorization: `Bearer ${token}` };
      const [queueResponse, auditResponse] = await Promise.all([
        apiRequest<{ submissions: Submission[] }>("/reviewer/submissions", { headers }),
        apiRequest<{ audit: Array<Record<string, string>> }>("/reviewer/audit", { headers }),
      ]);
      setQueue(queueResponse.submissions); setAudit(auditResponse.audit); setReady(true);
      sessionStorage.setItem("pkl_reviewer_token", token); sessionStorage.setItem("pkl_reviewer_id", reviewerId);
    } catch (requestError) { setReady(false); setError(requestError instanceof Error ? requestError.message : "Reviewer authentication failed."); }
  }

  async function decide(id: string, status: "accepted" | "rejected") {
    try {
      await apiRequest(`/reviewer/submissions/${encodeURIComponent(id)}/decision`, {
        method: "POST", headers: { Authorization: `Bearer ${token}` },
        body: JSON.stringify({ status, reviewer_id: reviewerId, note: status === "accepted" ? "Accepted after reviewer assessment." : "Rejected after reviewer assessment." }),
      });
      await load();
    } catch (requestError) { setError(requestError instanceof Error ? requestError.message : "Moderation failed."); }
  }

  return <main className="reviewer-page"><section className="claim-form-card">
    <p className="eyebrow">REVIEWER CONSOLE</p><h1>Moderate submissions.</h1><p className="form-intro">Only authenticated reviewers can see pending submissions or change publication state.</p>
    <div className="reviewer-login"><label>Reviewer token<input type="password" value={token} onChange={(event) => setToken(event.target.value)} /></label><label>Reviewer ID<input value={reviewerId} onChange={(event) => setReviewerId(event.target.value)} placeholder="e.g. reviewer-1" /></label><button className="primary-button" onClick={load} type="button">Open queue</button></div>
    {error && <p className="error-message" role="alert">{error}</p>}
    {ready && <>
      <h2>Pending review ({queue.length})</h2>
      <div className="review-queue">{queue.map((item) => <article className="review-card" key={item.id}><p className="pkl-id">{item.id}</p><h2>{item.title}</h2><p><strong>{item.category}</strong></p><p>{item.statement}</p><p>Submitted by: {item.contributor_id || "anonymous"}</p><div className="form-actions"><button className="secondary-button" onClick={() => decide(item.id, "rejected")} type="button">Reject</button><button className="primary-button" onClick={() => decide(item.id, "accepted")} type="button">Accept & publish</button></div></article>)}{queue.length === 0 && <p>No pending submissions.</p>}</div>
      <h2>Audit trail</h2><div className="audit-list">{audit.slice().reverse().map((event, index) => <p key={`${event.submission_id}-${event.at}-${index}`}><strong>{event.action}</strong> — {event.submission_id} — {event.reviewer_id || "system"} — {event.at}</p>)}</div>
    </>}
    <button className="secondary-button" onClick={onBack} type="button">Back to home</button>
  </section></main>;
}

function App() {
  const [page, setPage] = useState<"home" | "browse" | "claim" | "submit" | "reviewers" | "reviewer">(() => window.location.pathname === "/reviewers" ? "reviewers" : "home");
  const [selected, setSelected] = useState<Claim>(seedClaims[0]);
  const [claims, setClaims] = useState<Claim[]>(seedClaims);
  const [notice, setNotice] = useState("");

  useEffect(() => {
    apiRequest<{ submissions: Submission[] }>("/public/submissions")
      .then(({ submissions }) => setClaims([...seedClaims, ...submissions]))
      .catch(() => setClaims(seedClaims));
  }, []);

  if (page === "browse") return <Browse claims={claims} onSelect={(claim) => { setSelected(claim); setPage("claim"); }} onBack={() => setPage("home")} />;
  if (page === "claim") return <><header className="site-header"><button className="back-button" onClick={() => setPage("browse")} type="button">← Public Knowledge Ledger</button></header><ClaimRecord {...selected} /></>;
  if (page === "submit") return <><header className="site-header"><button className="back-button" onClick={() => setPage("home")} type="button">← Public Knowledge Ledger</button></header><ClaimForm onCancel={() => setPage("home")} onSubmitted={(message) => { setNotice(message); setPage("home"); }} /></>;
  if (page === "reviewers") return <ReviewerRecruitment onBack={() => { window.history.pushState({}, "", "/"); setPage("home"); }} onConsole={() => setPage("reviewer")} />;
  if (page === "reviewer") return <><header className="site-header"><button className="back-button" onClick={() => setPage("home")} type="button">← Public Knowledge Ledger</button></header><Reviewer onBack={() => setPage("home")} /></>;
  return <><Home onBrowse={() => setPage("browse")} onSubmit={() => setPage("submit")} onReviewer={() => { window.history.pushState({}, "", "/reviewers"); setPage("reviewers"); }} />{notice && <div className="notice" role="status">{notice}<button onClick={() => setNotice("")} type="button">Dismiss</button></div>}</>;
}

export default App;
