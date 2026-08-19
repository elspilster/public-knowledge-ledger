# Public Knowledge Ledger — Initial Specification

**Version:** v0.1
**Status:** Draft

## 1. Overview

PKL is an auditable knowledge system in which claims are linked to evidence, provenance, challenges, verification events, and assessment history.

The system must preserve the distinction between:

1. the claim itself;
2. the quality of individual evidence;
3. the independence of evidence;
4. whether evidence supports or contradicts the claim; and
5. the historical reliability of the contributor.

## 2. Claim

A claim is a statement that can be evaluated against evidence.

A claim should have:

- a stable identifier;
- the claim text;
- creation timestamp;
- current assessment;
- linked evidence;
- linked challenges;
- provenance/history;
- status such as proposed, supported, disputed, uncertain, superseded, or rejected.

## 3. Evidence

Evidence is a record that may support, contradict, qualify, or contextualise a claim.

An evidence record should capture, where available:

- source;
- author/contributor;
- date;
- methodology;
- data or observation;
- relevant context;
- conflicts of interest;
- transparency/accessibility;
- relationship to other evidence;
- reviewer assessments.

## 4. Evidence Profile

PKL should avoid reducing evidence to one opaque score. Important dimensions should be independently recorded, including:

- methodology quality;
- source quality;
- independence;
- replication;
- sample/data strength;
- bias risk;
- transparency;
- predictive success;
- contradictory evidence;
- relevance to the claim.

An overall assessment may be derived from these dimensions, but the underlying dimensions remain visible.

## 5. Evidence Levels

The original PKL scale is retained as a coarse summary, not as a replacement for the Evidence Profile:

- **E0** — assertion/no supporting evidence
- **E1** — anecdotal observation
- **E2** — repeated observation
- **E3** — independent reproduction/confirmation
- **E4** — successful predictive testing
- **E5** — convergent, independently supported evidence with reproducible results and no credible contradictory evidence sufficient to overturn the assessment

The E-level must not conceal important weaknesses in individual evidence dimensions.

## 6. Independence validation

PKL should explicitly assess whether evidence is genuinely independent.

Suggested levels:

- **I0** — independence unknown
- **I1** — evidence is materially dependent on the same underlying source
- **I2** — partly independent; significant shared sources, data, assumptions, or methods
- **I3** — independently produced evidence
- **I4** — strongly independent evidence using substantially independent investigators, data, methods, or sources that converge on the relevant result

Different publications do not automatically constitute independent evidence. Provenance should be traced where possible.

## 7. Challenges

Any participant may submit a challenge containing reasoning or counter-evidence.

A challenge must not silently alter the original record. It becomes part of the claim history and may change the current assessment after review.

A failed replication does not automatically prove a claim false; methodological differences and alternative explanations must be recorded.

## 8. Contributor reputation

Contributor reputation measures demonstrated historical reliability, not truth authority.

Reputation should consider factors such as:

- independently verified submissions;
- accuracy of previous assessments;
- corrections;
- transparency;
- quality of collaboration;
- successful challenges;
- false or unsupported submissions.

Reputation must not determine whether a new piece of evidence is true.

Reputation should be multidimensional where practical and should be capable of changing over time.

## 9. Review

Evidence should be independently reviewed where practical. Blind review should be used where practical to reduce authority bias.

A contributor may propose an evidence rating, but the proposer does not have unilateral authority to assign the final rating.

## 10. Provenance graph

Evidence relationships should be representable as a graph so PKL can distinguish independent evidence from repeated copies or derivative reporting.

Example:

```text
Evidence A -> Original study X
Evidence B -> Independent study Y
Evidence C -> Article citing study X
```

A and B may be independent. C should not automatically count as a third independent confirmation.

## 11. History and auditability

Material changes should create a new historical event rather than overwriting the meaning of prior events. The system should support cryptographic integrity checks for the event history.

## 12. Current design principle

> Count independent evidence, not repeated claims.

## 13. Open questions

The following remain deliberately unresolved and require testing before v1.0:

- exact reputation mathematics;
- exact aggregation of Evidence Profile dimensions;
- governance and rule-change procedure;
- cryptographic identity design;
- database schema and API contract;
- privacy and redaction rules;
- abuse resistance and Sybil resistance;
- dispute resolution when reviewers remain divided.
