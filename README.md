# Public Knowledge Ledger (PKL)

**Public Knowledge Ledger** is an open project for recording claims, evidence, challenges, provenance, verification, uncertainty, and contributor track records in an auditable knowledge system.

## Core principle

> **Don't trust the person. Don't trust the AI. Follow the evidence.**

PKL distinguishes evidence quality from contributor reputation, records independent evidence and disagreement, preserves correction history, and avoids treating consensus or authority as proof of truth.

## Current status

**Version:** v1 security baseline / working prototype

The core ledger, cryptographic key lifecycle, provenance graph, replay verification, quorum policy, auditable root-council decisions, explainable claim queries, public frontend, persistent submission workflow, moderation API, and reviewer console are implemented in the current development slice.

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
- Submission -> review -> publication lifecycle

## Public submission API

The M9 submission layer deliberately separates **proposal from publication**. `POST /api/submissions` creates a pending record. `GET /api/public/submissions` returns accepted records only. Pending, rejected, and withdrawn submissions never appear in the public projection.

`GET /api/health` verifies that the deployed function can read its durable store. `GET /api/v1/claims` is the stable, versioned public integration endpoint. Internal contributor, rate-limit, and reviewer-note fields are removed from all public projections.

Commercial API access is not enabled yet. PKL will keep core public access available and charge later for higher limits, monitoring, private workspaces, support, and service commitments—not for favourable assessment outcomes.

The API is implemented without a mandatory web-framework dependency, so it can run locally with the Python standard library:

```powershell
$env:PKL_REVIEWER_TOKEN = "replace-with-a-long-random-secret"
python -m pkl.server
```

The local API listens on `http://127.0.0.1:8787` by default. During frontend development, Vite proxies `/api` to that address. For a production deployment, place the API behind HTTPS and a reverse proxy, and set `VITE_PKL_API_URL` to the public API origin/path as appropriate.

## Reviewer workflow

Open **Reviewer access** in the frontend and provide the server-side `PKL_REVIEWER_TOKEN` plus a reviewer ID. Authenticated reviewers can inspect the pending queue, accept or reject submissions, and inspect the moderation audit trail.

The reviewer token is never stored in the repository. The browser keeps it only in session storage for the current session.

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
- `frontend/` — public React/Vite working model
- `tests/` — automated tests

## Security posture

PKL's security work is adversarial rather than trust-based. The test suite covers signature validation, key lifecycle and rotation, replay/tamper detection, quorum invariants, root-of-trust delegation, provenance conflicts, submission abuse controls, moderation boundaries, and public/private visibility.

## Contributing

PKL itself is subject to challenge. Proposed changes should explain what problem they solve, what evidence supports them, and what trade-offs they introduce.
