# M3–M5 implementation checkpoint

This branch is an intentionally bounded parallel implementation slice.

## M3
- Corrections append `claim.corrected` events and preserve the original claim event.
- Assessments append immutable history entries.
- Challenges can be resolved exactly once.
- Reviewer positions are retained independently so disagreement is not collapsed.
- Replay reconstructs corrections, challenge resolution, assessment history, and reviews.

## M4
- `ingest_source()` records caller-supplied source material as evidence.
- Source identity and extraction context are retained as metadata.
- SHA-256 identifies the exact supplied source content.
- Missing metadata is represented as missing; the ingestion layer does not invent it or fetch URLs.

## M5
- `KnowledgeQuery` uses the ledger provenance graph by default.
- Claim inspection exposes evidence, challenges, assessment history, reviewer positions, provenance, and audit history.

## Verification gate
The branch is not considered complete until the full test suite and CI pass on the branch and the acceptance criteria are reviewed against the resulting behaviour.
