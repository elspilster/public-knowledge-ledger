# PKL Roadmap Status

Updated 2026-08-25.

## Verified complete

- **M0–M6:** core ledger, evidence/provenance, assessment, disputes/corrections, ingestion/query foundations, and adversarial trust-boundary hardening are present in the repository and covered by the existing test suite.
- **M8:** public frontend vertical slice is merged to `main` as PR #13. It provides a landing page, selectable ledger entries, search by ID/title/category/text, record inspection, and review-gated claim submission.
- **M8 verification:** the backend test suite passed and the frontend CI passed after adding the Vite client type declaration required by TypeScript 6.

## Active

- **M9 — persistent submissions, moderation, and abuse resistance:** issue #14 and draft PR #15.

M9's first slice adds a dependency-free JSON-backed submission store with:

- stable submission IDs and timestamps;
- `pending_review`, `accepted`, `rejected`, and `withdrawn` states;
- reviewer audit entries;
- public visibility restricted to accepted submissions;
- required-field and length validation;
- duplicate detection;
- per-contributor rate limiting;
- automated lifecycle and abuse-control tests.

The next M9 increment is the adapter layer: authenticated API endpoints, reviewer controls, and wiring the public frontend to the durable store.

## Remaining path to a credible PKL v1

1. Finish M9 adapter/API and moderation UI.
2. Run real end-to-end submission → review → acceptance/rejection flows.
3. Complete privacy/redaction and contributor-identity safeguards.
4. Validate the model against a small real-world corpus and adversarial cases.
5. Document known limits, especially Sybil resistance, collusion, reviewer legitimacy, and automated-assessment limits.
6. Keep every milestone gated by tests, replay/audit coverage where state changes, documentation, and green CI.

PKL should not declare itself "finished" merely because the UI is complete. The release bar is an independently inspectable system in which submissions, evidence, provenance, disagreement, moderation, and historical changes remain traceable.
