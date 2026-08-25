import { useMemo, useState } from "react";
import { ClaimRecord } from "./pages/ClaimRecord";
import type { Claim } from "./types/claim";
import "./App.css";

const seedClaims: Claim[] = [
  {
    id: "PKL-BIO-001",
    title: "DNA encodes hereditary genetic information",
    statement:
      "DNA contains the biological information used to store and transmit hereditary information in living organisms.",
    category: "Molecular Biology",
    status: "Established",
    evidence: [
      "Experimental evidence from molecular genetics",
      "DNA structure research and sequencing evidence",
      "Functional evidence linking genes to inherited traits",
    ],
    limitations: [
      "DNA is not the only factor influencing biological traits",
      "Gene regulation affects how information is expressed",
      "Biological systems involve complex interactions",
    ],
    relationships: ["Evolution", "Genetic variation", "Epigenetics"],
  },
  {
    id: "PKL-PHY-001",
    title: "Objects near Earth's surface accelerate downward",
    statement:
      "In the absence of significant air resistance, objects near Earth's surface experience approximately uniform downward gravitational acceleration.",
    category: "Physics",
    status: "Established",
    evidence: [
      "Repeated experimental measurements of gravitational acceleration",
      "Classical mechanics and modern gravitational theory",
    ],
    limitations: [
      "The approximation varies with altitude and location",
      "Air resistance changes the motion of many real objects",
    ],
    relationships: ["Gravity", "Classical mechanics", "General relativity"],
  },
  {
    id: "PKL-EAR-001",
    title: "Earth's climate has changed throughout geological history",
    statement:
      "Earth's climate has varied substantially over geological time as a result of interacting physical, chemical, biological, and astronomical factors.",
    category: "Earth Science",
    status: "Established",
    evidence: [
      "Ice-core, sediment, fossil, and isotope records",
      "Multiple independent paleoclimate reconstructions",
    ],
    limitations: [
      "Past climate records have different resolutions and uncertainties",
      "The causes and timing of individual climate transitions can remain disputed",
    ],
    relationships: ["Paleoclimate", "Carbon cycle", "Atmospheric composition"],
  },
];

function Home({ onBrowse, onSubmit }: { onBrowse: () => void; onSubmit: () => void }) {
  return (
    <main className="landing-page">
      <section className="hero">
        <p className="eyebrow">PUBLIC KNOWLEDGE LEDGER</p>
        <h1>
          Knowledge should
          <br />
          <span>be traceable.</span>
        </h1>
        <p className="hero-text">
          A public ledger for recording claims, evidence, limitations,
          relationships, and the current state of knowledge.
        </p>
        <div className="hero-actions">
          <button className="primary-button" onClick={onBrowse}>Browse the ledger</button>
          <button className="secondary-button" onClick={onSubmit} type="button">Submit a claim</button>
        </div>
      </section>
      <section className="principles">
        <article><h2>Claims</h2><p>Clear statements of what is being claimed.</p></article>
        <article><h2>Evidence</h2><p>A visible trail showing what supports a claim.</p></article>
        <article><h2>Uncertainty</h2><p>Limitations and unanswered questions remain part of the record.</p></article>
      </section>
      <section className="about-ledger">
        <p className="eyebrow">THE LEDGER</p>
        <h2>Knowledge is allowed to change.</h2>
        <p>PKL records are evidence assessments at a particular point in time. New evidence can strengthen, weaken, revise, or overturn an assessment.</p>
      </section>
    </main>
  );
}

function Browse({ claims, onSelect, onBack }: { claims: Claim[]; onSelect: (claim: Claim) => void; onBack: () => void }) {
  const [query, setQuery] = useState("");
  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return claims;
    return claims.filter((claim) => [claim.id, claim.title, claim.category, claim.statement].join(" ").toLowerCase().includes(q));
  }, [claims, query]);

  return (
    <main className="browse-page">
      <section className="browse-header">
        <p className="eyebrow">THE LEDGER</p>
        <h1>Browse knowledge records.</h1>
        <input aria-label="Search claims" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search by title, category, ID, or text…" />
      </section>
      <section className="claim-list">
        {filtered.map((claim) => (
          <button className="claim-card" key={claim.id} onClick={() => onSelect(claim)} type="button">
            <p>{claim.id}</p><h2>{claim.title}</h2><p>{claim.category}</p><strong>{claim.status}</strong><p>{claim.statement}</p>
          </button>
        ))}
        {filtered.length === 0 && <p>No matching records found.</p>}
      </section>
      <button className="secondary-button" onClick={onBack} type="button">Back to home</button>
    </main>
  );
}

function ClaimForm({ onCancel, onSubmitted }: { onCancel: () => void; onSubmitted: () => void }) {
  const [title, setTitle] = useState("");
  const [statement, setStatement] = useState("");
  const [category, setCategory] = useState("");
  const [evidence, setEvidence] = useState("");
  const [limitations, setLimitations] = useState("");
  const [relationships, setRelationships] = useState("");

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onSubmitted();
  }

  return (
    <main className="claim-form-page"><section className="claim-form-card">
      <p className="eyebrow">SUBMIT A CLAIM</p><h1>Propose a knowledge record.</h1>
      <p className="form-intro">Submissions enter review and are not published directly to the public ledger.</p>
      <form onSubmit={handleSubmit}>
        <label>Claim title<input value={title} onChange={(e) => setTitle(e.target.value)} required /></label>
        <label>Statement<textarea value={statement} onChange={(e) => setStatement(e.target.value)} rows={5} required /></label>
        <label>Category<input value={category} onChange={(e) => setCategory(e.target.value)} required /></label>
        <label>Evidence<textarea value={evidence} onChange={(e) => setEvidence(e.target.value)} rows={5} /></label>
        <label>Known limitations<textarea value={limitations} onChange={(e) => setLimitations(e.target.value)} rows={5} /></label>
        <label>Related knowledge<textarea value={relationships} onChange={(e) => setRelationships(e.target.value)} rows={4} /></label>
        <div className="form-actions"><button className="secondary-button" onClick={onCancel} type="button">Cancel</button><button className="primary-button" type="submit">Submit for review</button></div>
      </form>
    </section></main>
  );
}

function App() {
  const [page, setPage] = useState<"home" | "browse" | "claim" | "submit">("home");
  const [selectedClaim, setSelectedClaim] = useState<Claim>(seedClaims[0]);

  if (page === "browse") return <Browse claims={seedClaims} onSelect={(claim) => { setSelectedClaim(claim); setPage("claim"); }} onBack={() => setPage("home")} />;
  if (page === "claim") return <><header className="site-header"><button className="back-button" onClick={() => setPage("browse")} type="button">← Public Knowledge Ledger</button></header><ClaimRecord {...selectedClaim} /></>;
  if (page === "submit") return <><header className="site-header"><button className="back-button" onClick={() => setPage("home")} type="button">← Public Knowledge Ledger</button></header><ClaimForm onCancel={() => setPage("home")} onSubmitted={() => setPage("browse")} /></>;
  return <Home onBrowse={() => setPage("browse")} onSubmit={() => setPage("submit")} />;
}

export default App;
