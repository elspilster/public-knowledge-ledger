export type ClaimStatus = "established" | "reviewed" | "uncertain" | "proposed";

export type ClaimType =
  | "observation"
  | "causal"
  | "mechanism"
  | "prediction"
  | "historical"
  | "uncertain";

export interface Claim {
  id: string;
  title: string;
  statement: string;
  category: string;
  claimType: ClaimType;
  status: ClaimStatus;
  evidence: string[];
  limitations: string[];
  relationships: string[];
}
