# Public Knowledge Ledger (PKL)

**Public Knowledge Ledger** is an open project for recording claims, evidence, challenges, provenance, verification, uncertainty, and contributor track records in an auditable knowledge system.

## Core principle

> **Don't trust the person. Don't trust the AI. Follow the evidence.**

PKL distinguishes evidence quality from contributor reputation, records independent evidence and disagreement, preserves correction history, and avoids treating consensus or authority as proof of truth.

## Current status

**Version:** v1 security baseline / working prototype

The core ledger, cryptographic key lifecycle, provenance graph, replay verification, quorum policy, auditable root-council decisions, and explainable claim queries are implemented and covered by automated tests.

The system is experimental and does not claim to provide absolute truth. Cryptographic authentication proves that a credential signed an event; it does **not** prove that the claim is true.

## Core concepts

- Claims
- Evidence and evidence profiles
- Provenance and independence assessment
- Challenges and counter-evidence
- Independent verification
- Contributor and cryptographic key identities
- Key rotation and revocation
- Transparent correction history
- Cryptographically auditable records
- Explicit uncertainty and disagreement
- 4-of-N style root-council quorum
- Auditable council decisions
- Explainable claim queries
- Human and AI participation without automatic authority

## Explain a claim

The `KnowledgeQuery` API exposes a structured explanation containing the claim, assessment, evidence, provenance edges, challenges, council decision, and ledger history.

```python
from pkl import KnowledgeQuery

explanation = KnowledgeQuery(ledger, provenance, council).explain(claim_id)
```

The response deliberately includes `authenticated_is_not_true: True` to make the epistemic boundary explicit.

## Repository structure

- `CONSTITUTION.md` — foundational principles
- `SPECIFICATION.md` — technical and data-model direction
- `docs/` — focused design documents
- `pkl/` — implementation
- `tests/` — automated tests

## Security posture

PKL's security work is adversarial rather than trust-based. The test suite covers signature validation, key lifecycle and rotation, replay/tamper detection, quorum invariants, root-of-trust delegation, provenance conflicts, and council quorum behaviour.

## Contributing

PKL itself is subject to challenge. Proposed changes should explain what problem they solve, what evidence supports them, and what trade-offs they introduce.
