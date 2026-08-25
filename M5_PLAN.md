# Public Knowledge Ledger — M5 Plan

**Milestone:** M5 — Query and inspection API  
**Status:** Planned

## Hypothesis

PKL's value is testable only if an independent observer can retrieve a claim and inspect the evidence, provenance, contradictions, assessment reasoning, and history behind it without needing internal implementation knowledge.

## Goal

Expose a small, read-oriented query contract over the stable ledger model. The first API should make PKL inspectable rather than attempt to become a full application platform.

## Core query contract

An observer should be able to retrieve a claim and, from one navigable response or a small set of deterministic queries, inspect:

- claim identity and current content;
- current assessment;
- assessment explanation/reasoning;
- supporting evidence;
- contradicting evidence;
- provenance families / independence relationships;
- correlation and conflict-of-interest disclosures;
- Evidence Profile dimensions where recorded;
- challenges and disputes;
- corrections and assessment transitions;
- historical assessment states;
- ledger/event identifiers needed for audit or replay verification.

Exact field names and transport format should follow the existing repository model. The API contract should not duplicate or redefine the ledger's source of truth.

## Proposed operations

Start with the minimum read surface:

- `get claim by id`
- `list claims` with bounded filtering/pagination
- `get claim assessment history`
- `get evidence by id`
- `get event / audit record by id`

A write API is not required for M5 unless implementation experience shows a narrow operation is necessary for the milestone's end-to-end validation.

## Invariants

- **Read results are derived from ledger state.** The API must not maintain a second authoritative assessment store.
- **Disagreement remains visible.** Queries must not collapse contradictory evidence or unresolved disputes into a single clean narrative.
- **Provenance remains inspectable.** The observer can determine why evidence was or was not treated as independent.
- **History is preserved.** Current state and historical transitions are distinguishable.
- **Determinism matters.** Equivalent ledger state should yield stable, documented representations.
- **Authorization does not rewrite truth.** Access control may hide data where required, but it must not silently alter the underlying assessment semantics.
- **No opaque confidence score.** The API exposes structured assessment reasoning and Evidence Profile information rather than inventing a single numerical truth value.

## Acceptance tests

M5 is complete when automated and integration tests demonstrate:

1. retrieving a known claim by identifier;
2. retrieving its current assessment;
3. retrieving supporting and contradicting evidence;
4. inspecting provenance-family relationships;
5. inspecting Evidence Profile information where present;
6. retrieving assessment history and explaining at least one transition;
7. retrieving an unresolved and a resolved dispute state;
8. retrieving audit/event identifiers sufficient to verify the relevant history;
9. bounded list/query behaviour that does not expose unbounded resource usage;
10. an adversarial test proving that a query cannot silently omit contradictory evidence from a result presented as a complete assessment view.

## Non-goals

M5 should not introduce:

- a complex frontend;
- distributed search infrastructure;
- broad authentication/identity federation;
- automated moderation;
- recommendation/ranking systems that imply truth authority;
- a second mutable database that becomes authoritative over the ledger.

## Failure gates

Stop and reassess if the API design requires:

- duplicating assessment logic outside the ledger model;
- hiding contradiction or dispute state to make responses cleaner;
- an opaque confidence score;
- unbounded queries over the complete ledger;
- mutable API-side state that cannot be reconstructed from ledger events.

## Design rule

> **The query layer should make PKL easier to inspect, not make the underlying epistemic record less inspectable.**
