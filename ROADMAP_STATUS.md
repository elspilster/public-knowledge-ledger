# PKL Roadmap Status

Updated 2026-08-25.

## Verified complete

- **M0–M6:** core ledger, evidence/provenance, assessment, disputes/corrections, ingestion/query foundations, and adversarial trust-boundary hardening are present in the repository and covered by the existing test suite.
- **M8:** public frontend vertical slice is merged to `main` as PR #13. It provides a landing page, selectable ledger entries, search by ID/title/category/text, record inspection, and review-gated claim submission.
- **M8 verification:** backend tests and frontend CI passed.
- **M9:** persistent submission, moderation, abuse-control, API, and reviewer workflow is complete in `main` as PRs #15 and #17.

### M9 verified surface

- JSON-backed durable submission store;
- stable submission IDs and timestamps;
- explicit `pending_review`, `accepted`, `rejected`, and `withdrawn` states;
- reviewer audit trail;
- accepted-only public projection;
- validation, duplicate detection, and rate limiting;
- server-observed IP rate limiting for the HTTP surface;
- stable JSON error codes for validation, duplicates, rate limits, authentication, missing records, and invalid transitions;
- authenticated reviewer queue and accept/reject actions;
- reviewer audit visibility;
- React submission form wired to the API rather than browser-only storage;
- public browse view automatically includes accepted submissions;
- local Vite-to-API proxy and documented API server operation;
- integration tests covering submission → review → accept/reject → public visibility and persistence;
- green backend and frontend CI on the M9.1 merge commit.

## Remaining path to a credible PKL v1

1. Run real end-to-end submission → review → acceptance/rejection flows against the deployed service.
2. Complete production privacy/redaction and contributor-identity safeguards.
3. Validate the model against a small real-world corpus and adversarial cases.
4. Document known limits, especially Sybil resistance, collusion, reviewer legitimacy, and automated-assessment limits.
5. Keep every milestone gated by tests, replay/audit coverage where state changes, documentation, and green CI.

PKL should not declare itself "finished" merely because the UI is complete. The release bar is an independently inspectable system in which submissions, evidence, provenance, disagreement, moderation, and historical changes remain traceable.
