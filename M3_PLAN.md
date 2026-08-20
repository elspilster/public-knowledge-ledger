# Public Knowledge Ledger — M3 Plan

**Milestone:** M3 — Disputes, corrections, and assessment history  
**Status:** Planned

## Goal

Make changes to a claim assessment first-class, auditable, and inspectable without rewriting the historical record.

## Scope

M3 should provide a small complete vertical slice covering:

1. **Challenges** — a participant can challenge an existing assessment with reasoning and/or counter-evidence.
2. **Assessment changes** — new evidence can cause a claim's current assessment to change.
3. **Corrections** — previously recorded information can be corrected by adding new history rather than silently mutating the old record.
4. **Reviewer/council disagreement** — disagreement about an assessment can remain visible instead of being collapsed into a false consensus.
5. **Historical comparison** — observers can inspect how and why an assessment changed over time.
6. **Resolution state** — disputes can be explicitly resolved or remain unresolved.
7. **Replay/auditability** — all state-changing behaviour remains replayable and cryptographically/audit verifiably recorded.

## Non-goals

M3 should not introduce:

- a new opaque confidence score;
- complex governance machinery;
- reputation-based truth authority;
- broad automated source ingestion;
- a frontend or API layer ahead of the underlying model.

## Acceptance criteria

M3 is complete when the repository has automated tests and an end-to-end fixture demonstrating:

- an initial assessment;
- a challenge against that assessment;
- additional supporting or contradicting evidence;
- an assessment transition;
- preserved historical assessment state;
- a correction represented as a new event;
- reviewer/council disagreement where applicable;
- explicit resolved and unresolved dispute states;
- successful ledger replay with the resulting current state matching the recorded history.

The tests should include at least one adversarial case ensuring a correction cannot erase or rewrite the meaning of an earlier event.

## Design rule

> **Correction changes the current state by adding history; it never rewrites history.**

The M3 implementation should remain a small vertical slice and should expose uncertainty and disagreement rather than hiding them behind a single verdict.
