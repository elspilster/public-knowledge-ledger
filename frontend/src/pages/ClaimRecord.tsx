export type ClaimRecordProps = {
  id: string;
  title: string;
  statement: string;
  category: string;
  status: string;
  evidence: string[];
  limitations: string[];
  relationships: string[];
};

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="pkl-section">
      <h2>{title}</h2>
      {children}
    </section>
  );
}

export function ClaimRecord({
  id,
  title,
  statement,
  category,
  status,
  evidence,
  limitations,
  relationships,
}: ClaimRecordProps) {
  return (
    <main className="pkl-record">
      <header className="pkl-header">
        <p className="pkl-id">{id}</p>
        <h1>{title}</h1>
        <p>{category}</p>
        <strong className="pkl-status">{status}</strong>
      </header>

      <Section title="Claim">
        <p className="pkl-statement">{statement}</p>
      </Section>

      <Section title="Evidence trail">
        <ul>
          {evidence.map((item) => <li key={item}>{item}</li>)}
        </ul>
      </Section>

      <Section title="Known limitations">
        <ul>
          {limitations.map((item) => <li key={item}>{item}</li>)}
        </ul>
      </Section>

      <Section title="Related knowledge">
        <ul>
          {relationships.map((item) => <li key={item}>{item}</li>)}
        </ul>
      </Section>

      <Section title="Record note">
        <p>
          This PKL record represents a current evidence assessment and may be
          revised as new evidence emerges.
        </p>
      </Section>
    </main>
  );
}
