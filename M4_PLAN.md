# Public Knowledge Ledger — M4 Plan

**Milestone:** M4 — Practical source ingestion  
**Status:** Planned

## Hypothesis

PKL becomes materially more useful when a real-world source can be represented as evidence, linked to provenance and a claim, and assessed without losing the source's identity or limitations.

## Goal

Build the smallest practical ingestion path:

`Source → Evidence → Provenance → Claim → Assessment`

The aim is not broad web crawling. It is a trustworthy, inspectable path from a concrete source to a claim assessment.

## Scope

M4 should support a deliberately small set of source types and a deterministic ingestion workflow.

### Minimum source record

A source should retain enough information to identify and later re-check it, including where applicable:

- source URI or stable locator;
- title/name;
- publisher or author;
- publication date when available;
- retrieval date/time;
- source type;
- content or a content-derived integrity identifier;
- extraction method/version;
- relevant excerpt or evidence payload;
- provenance metadata;
- known correlation/conflict information where available.

Exact fields must follow the existing schema conventions rather than introducing duplicate representations.

### Minimum ingestion flow

1. accept a concrete source;
2. record source metadata;
3. extract a bounded evidence item;
4. attach provenance;
5. link the evidence to an existing claim or create a new claim explicitly;
6. run the existing M2 assessment machinery;
7. preserve the ingestion and assessment events in the ledger;
8. expose enough metadata to reproduce or inspect the derivation.

## Invariants

- **Source identity is preserved.** Evidence must not become detached from the source it came from.
- **Extraction is explicit.** The system records how evidence was derived from the source.
- **No silent paraphrase.** If the stored evidence is transformed, the transformation is identifiable.
- **Provenance remains inspectable.** Ingestion must not flatten provenance into a single anonymous source label.
- **M2 semantics are reused.** Ingestion does not bypass provenance-family, correlation, contradiction, or assessment rules.
- **Unavailable information stays unavailable.** Missing metadata is represented as missing rather than guessed.
- **Replay remains possible.** Ingestion events can be validated and replayed without requiring hidden mutable state.

## Acceptance tests

M4 is complete when an end-to-end fixture demonstrates:

1. ingesting at least one concrete source;
2. recording its source metadata and retrieval context;
3. extracting bounded evidence from it;
4. linking that evidence to a claim;
5. generating the expected provenance relationship;
6. producing an M2-compatible assessment;
7. preserving the source/evidence/claim relationship after ledger replay;
8. detecting or representing a changed source where integrity metadata permits comparison;
9. handling missing source metadata without fabricating values;
10. an adversarial case showing that an altered source/excerpt cannot silently masquerade as the original evidence.

## Non-goals

M4 should not introduce:

- unrestricted web crawling;
- autonomous source selection as a truth authority;
- opaque source-quality scores;
- large-scale search infrastructure;
- a frontend;
- a public API before the underlying data contract is stable.

## Failure gates

Stop and reassess if ingestion requires:

- silently inventing missing source metadata;
- treating retrieval as proof of truth;
- losing source identity or extraction provenance;
- bypassing existing M2 assessment rules;
- storing transformed evidence without identifying the transformation.

## Design rule

> **Ingestion records what a source said, where it came from, how it was extracted, and how it entered the ledger; it does not turn retrieval into truth.**
