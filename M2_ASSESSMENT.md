# Public Knowledge Ledger — M2 Assessment

**Milestone:** M2 — Claim assessment  
**Status:** Complete / signed off  
**Assessment date:** 2026-08-20

## Scope

M2 delivers the smallest complete claim-assessment vertical slice: identify supporting and contradicting evidence, account for provenance when considering independence, preserve disagreement, and explain the current assessment without collapsing the Evidence Profile into an opaque confidence score.

## Assessment

M2 is accepted within its declared scope.

The implementation provides:

- explicit support and contradiction relationships;
- provenance-family awareness when assessing independence;
- correlation and conflict-of-interest safeguards;
- explainable assessment state;
- preservation of contradictory evidence;
- deterministic/replayable assessment behaviour where practical;
- tests covering convergence, derivative reporting, contradiction, shared provenance, and related adversarial cases;
- inspectable Evidence Profile dimensions rather than a hidden aggregate confidence score.

## Verification

The local test suite passes cleanly:

- **95 passed**
- **0 failed**

The initial local failures were caused by the development environment missing the `cryptography` dependency. Installing the dependency resolved all 22 environment-related failures without source changes.

## Deliberate limitation

M2 does not yet use Evidence Profile quality dimensions to assign subjective weights to competing evidence. Consequently, evidence-family counts can produce an assessment that does not reflect every qualitative difference between strong and weak evidence.

This is accepted as an explicit limitation rather than addressed with an opaque confidence score. The specification leaves exact aggregation of Evidence Profile dimensions as an open question, and the project plan explicitly excludes an opaque single-number confidence score from M2.

A future milestone may investigate quality-aware aggregation, but any such rule must remain explainable, versioned, and independently inspectable.

## Decision

**M2: COMPLETE.**

The next milestone is **M3 — Disputes, corrections, and assessment history**.

M3 should add first-class handling for challenges, new evidence that changes an assessment, corrections, reviewer/council disagreement, historical comparison, and explicit resolved/unresolved states while preserving the append-only audit history.
