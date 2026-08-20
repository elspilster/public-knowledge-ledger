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
    <main>
      <header>
        <p>{id}</p>
        <h1>{title}</h1>
        <p>{category}</p>
        <strong>{status}</strong>
      </header>

      <section>
        <h2>Claim</h2>
        <p>{statement}</p>
      </section>

      <section>
        <h2>Evidence</h2>
        <ul>{evidence.map((item) => <li key={item}>{item}</li>)}</ul>
      </section>

      <section>
        <h2>Limitations</h2>
        <ul>{limitations.map((item) => <li key={item}>{item}</li>)}</ul>
      </section>

      <section>
        <h2>Related claims</h2>
        <ul>{relationships.map((item) => <li key={item}>{item}</li>)}</ul>
      </section>
    </main>
  );
}
