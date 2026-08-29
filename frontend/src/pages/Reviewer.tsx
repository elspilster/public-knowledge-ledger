import { useEffect, useState } from "react";

type Submission = {
  id: string;
  title: string;
  statement: string;
  category: string;
  evidence: string[];
  limitations: string[];
  relationships: string[];
  created_at: string;
  status: string;
};

export default function Reviewer() {
  const [token, setToken] = useState("");
  const [submissions, setSubmissions] = useState<Submission[]>([]);
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);

  async function load() {
    if (!token) return;
    setMessage("");
    const res = await fetch("/api/reviewer/submissions", {
      headers: { Authorization: `Bearer ${token}` },
    });
    const data = await res.json();
    if (!res.ok) return setMessage(data.error || "Unable to load submissions");
    setSubmissions(data.submissions || []);
  }

  async function decide(id: string, status: "accepted" | "rejected") {
    setBusy(true);
    setMessage("");
    try {
      const res = await fetch(`/api/reviewer/submissions/${encodeURIComponent(id)}/decision`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ status, reviewer_id: "kollin", note: `Reviewed by Kollin (${status}).` }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Review failed");
      setSubmissions((items) => items.filter((item) => item.id !== id));
      setMessage(`Submission ${status}.`);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Review failed");
    } finally {
      setBusy(false);
    }
  }

  useEffect(() => { if (token) load(); }, []);

  return (
    <main style={{ maxWidth: 900, margin: "40px auto", padding: 24, fontFamily: "system-ui" }}>
      <h1>PKL Reviewer Console</h1>
      <p>Review pending knowledge submissions before they become public.</p>
      <div style={{ display: "flex", gap: 8, marginBottom: 24 }}>
        <input type="password" placeholder="Reviewer token" value={token} onChange={(e) => setToken(e.target.value)} style={{ flex: 1, padding: 10 }} />
        <button onClick={load} disabled={!token || busy}>Load submissions</button>
      </div>
      {message && <p>{message}</p>}
      {submissions.length === 0 ? <p>No pending submissions.</p> : submissions.map((item) => (
        <article key={item.id} style={{ border: "1px solid #ccc", borderRadius: 10, padding: 20, marginBottom: 16 }}>
          <small>{item.id} · {item.category}</small>
          <h2>{item.title}</h2>
          <p>{item.statement}</p>
          {item.evidence?.length > 0 && <><h3>Evidence</h3><ul>{item.evidence.map((x, i) => <li key={i}>{x}</li>)}</ul></>}
          {item.limitations?.length > 0 && <><h3>Limitations</h3><ul>{item.limitations.map((x, i) => <li key={i}>{x}</li>)}</ul></>}
          <div style={{ display: "flex", gap: 10 }}>
            <button disabled={busy} onClick={() => decide(item.id, "accepted")}>Accept & publish</button>
            <button disabled={busy} onClick={() => decide(item.id, "rejected")}>Reject</button>
          </div>
        </article>
      ))}
    </main>
  );
}
