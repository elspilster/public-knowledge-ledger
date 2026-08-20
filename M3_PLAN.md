# Public Knowledge Ledger — M3 Plan

**Milestone:** M3 — Disputes, corrections, and assessment history  
**Status:** Planned

## Hypothesis

PKL should be able to change its current assessment when new evidence or a correction arrives **without rewriting the historical record**, and an independent observer should be able to explain the transition from one state to another.

## Goal

Make changes to a claim assessment first-class, auditable, and inspectable while preserving the append-only history.

## Scope

M3 is a deliberately small vertical slice covering:

1. **Challenges** — a participant can challenge an existing assessment with reasoning and/or counter-evidence.
2. **Assessment changes** — new evidence can cause a claim's current assessment to change.
3. **Corrections** — previously recorded information can be corrected by adding new history rather than silently mutating the old record.
4. **Reviewer/council disagreement** — disagreement about an assessment can remain visible instead of being collapsed into false consensus.
5. **Historical comparison** — observers can inspect what the assessment was, what it is now, and which events explain the transition.
6. **Resolution state** — disputes can be explicitly resolved or remain unresolved.
7. **Replay/auditability** — all state-changing behaviour remains replayable and cryptographically/audit verifiably recorded.

## Proposed event vocabulary

Use the smallest event set the existing ledger model can support. Names are provisional until implementation inspection confirms the repository's conventions:

- `assessment_created`
- `assessment_challenged`
- `evidence_added`
- `assessment_changed`
- `correction_recorded`
- `dispute_resolved`
- `dispute_reopened`

A correction should reference the event or claim state it corrects rather than replacing it.

## Invariants

- **History is append-only.** A later correction must never mutate or delete an earlier event.
- **Current state is derivable.** The current assessment must be reproducible by replaying the ledger.
- **Disagreement is preserved.** A challenge or contrary reviewer assessment remains inspectable even if the current assessment does not change.
- **Corrections are explicit.** A correction identifies what is being corrected and why.
- **Resolution is not erasure.** Resolving a dispute changes its state; it does not remove the dispute or its evidence.
- **No hidden authority.** M3 does not introduce reputation-based truth authority or an opaque confidence score.

## Acceptance tests

M3 is complete when automated tests and an end-to-end fixture demonstrate:

1. an initial claim assessment;
2. a challenge against that assessment;
3. additional supporting or contradicting evidence;
4. an assessment transition;
5. preservation of the previous assessment state;
6. a correction represented as a new event;
7. visible reviewer/council disagreement where applicable;
8. explicit resolved and unresolved dispute states;
9. successful ledger replay with current state matching the recorded history;
10. an adversarial case proving a correction cannot erase or rewrite the meaning of an earlier event;
11. deterministic serialization/hashing for the new event types.

## Non-goals

M3 should not introduce:

- a new opaque confidence score;
- complex governance machinery;
- reputation-based truth authority;
- broad automated source ingestion;
- a frontend or public API layer ahead of the underlying model.

## Failure gates

Stop and reassess the design if implementing M3 requires:

- mutating historical ledger events;
- silently replacing an assessment without an event explaining why;
- a subjective numerical confidence score;
- a large governance framework to resolve ordinary disputes;
- weakening cryptographic verification or replay guarantees.

## Design rule

> **Correction changes the current state by adding history; it never rewrites history.**

M3 should expose uncertainty and disagreement rather than hiding them behind a single verdict.