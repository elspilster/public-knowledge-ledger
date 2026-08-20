import type { Claim } from "../types/claim";

type Props = {
  claim: Claim;
};

export function ClaimCard({ claim }: Props) {
  return (
    <article className="claim-card">
      <p>{claim.id}</p>
      <h2>{claim.title}</h2>
      <p>{claim.category}</p>
      <strong>{claim.status}</strong>
      <p>{claim.statement}</p>
    </article>
  );
}
