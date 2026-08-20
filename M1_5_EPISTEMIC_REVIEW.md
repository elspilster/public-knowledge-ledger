# M1.5 — Epistemic Adversarial Review

## Purpose

M1.5 hardens PKL's epistemic model before claim-assessment logic is expanded.
It incorporates external adversarial review and makes explicit what the ledger
can establish versus what it cannot establish.

## Principles

1. **Provenance distinctness is not epistemic independence.** PKL can report
   whether known provenance dependencies were detected. It must not imply that
   absence of a recorded dependency proves absence of shared bias, incentives,
   methods, instruments, funding, or other hidden correlations.
2. **Assessments are derived, time-bound judgements.** An assessment describes
   the evidence currently recorded and the assessment process that produced it;
   it is not a declaration of metaphysical truth.
3. **Evidence properties and evidence relationships are separate.** Quality
   dimensions belong to evidence; contradiction, duplication, provenance and
   semantic relationships belong to relationships between evidence/claims.
4. **Scope is part of a claim.** Claims should be precise enough that their
   boundary conditions can be assessed.
5. **Unknown remains unknown.** The ledger must expose missing information rather
   than silently converting absence of data into positive evidence.

## Current terminology

The legacy `independence_level` field is retained for compatibility in v0.1,
but new code should use `provenance_distinctness` and the
`independence_limitations` metadata. `I0`–`I4` describe the strength of the
recorded provenance distinction only.

## Adversarial cases to test

- Two apparently separate studies share an undisclosed funder.
- Two studies use the same instrument or upstream dataset.
- Many identities submit evidence derived from one undisclosed source.
- A claim is semantically duplicated under slightly different wording.
- A council reaches quorum while a documented conflict of interest remains.
- A claim has strong support but the ledger cannot establish that relevant
  contradictory evidence was not omitted.

## M2 gate

Claim assessment should not treat `I3` or `I4` as proof of statistical or
causal independence. The assessment engine must preserve the distinction
between recorded provenance and unknown external dependencies.
