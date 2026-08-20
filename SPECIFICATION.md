# Public Knowledge Ledger — Initial Specification

**Version:** v0.1
**Status:** Draft

## 1. Overview

PKL is an auditable knowledge system in which claims are linked to evidence, provenance, challenges, verification events, and assessment history.

The system must preserve the distinction between:

1. the claim itself;
2. the quality of individual evidence;
3. recorded provenance distinctness of evidence;
4. whether evidence supports or contradicts the claim; and
5. the historical reliability of the contributor.

PKL does **not** claim that a ledger assessment establishes metaphysical or real-world truth. An assessment is a reproducible interpretation of the evidence and metadata currently recorded in PKL under a named assessment method.

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

A claim status is therefore a **current recorded assessment state**, not a declaration that the claim is objectively true or false.

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
- recorded provenance distinctness;
- replication;
- sample/data strength;
- bias risk;
- transparency;
- predictive success;
- contradictory evidence;
- relevance to the claim.

An overall assessment may be derived from these dimensions, but the underlying dimensions remain visible. A particular assessment engine may use only a subset of these dimensions; when it does, its scope and limitations must be explicit rather than implying that unused dimensions were evaluated.

## 5. Evidence Levels

The original PKL scale is retained as a coarse summary, not as a replacement for the Evidence Profile:

- **E0** — assertion/no supporting evidence
- **E1** — anecdotal observation
- **E2** — repeated observation
- **E3** — independently reproduced/confirmed evidence under the assessment method's recorded provenance rules
- **E4** — successful predictive testing
- **E5** — convergent, independently supported evidence with reproducible results and no credible contradictory evidence sufficient to overturn the assessment

The E-level must not conceal important weaknesses in individual evidence dimensions. An E-level is a summary produced by an assessment method, not a truth score.

## 6. Recorded provenance distinctness

PKL must distinguish **recorded provenance distinctness** from epistemic independence.

Recorded provenance distinctness describes the degree to which PKL's recorded provenance graph finds evidence to have separate origins, sources, or dependency chains. It does **not** establish that the evidence is epistemically independent in the wider world.

Suggested levels:

- **I0** — recorded distinctness unknown
- **I1** — evidence is materially dependent on the same recorded underlying source
- **I2** — partly distinct; significant shared recorded sources, data, or methods
- **I3** — separately produced within the recorded provenance graph
- **I4** — strongly distinct within the recorded provenance graph, using substantially separate recorded investigators, data, methods, or sources

Different publications do not automatically constitute distinct evidence. Provenance should be traced where possible. Hidden dependencies, shared incentives, common assumptions, undisclosed communications, and other relationships outside PKL's recorded data may remain undetected.

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

Evidence relationships should be representable as a graph so PKL can distinguish recorded provenance families from repeated copies or derivative reporting.

Example:

```text
Evidence A -> Original study X
Evidence B -> Independent study Y
Evidence C -> Article citing study X
```

A and B may be recorded as distinct. C should not automatically count as a third distinct confirmation.

## 11. History and auditability

Material changes should create a new historical event rather than overwriting the meaning of prior events. The system should support cryptographic integrity checks for the event history.

## 12. Current design principle

> Count recorded evidence families, not repeated claims — and state clearly what the assessment method actually measures.

## 13. Assessment and overview boundary

PKL distinguishes three layers:

1. **Evidence overview** — a structured description of the evidence, provenance, relationships, challenges, and limitations currently recorded.
2. **Derived assessment** — a deterministic or otherwise specified interpretation produced by a named assessment engine from that recorded state.
3. **Truth** — a property of the world that PKL does not establish merely by recording, authenticating, or assessing evidence.

M2 is an **assessment engine and evidence overview**, not a truth oracle. A consumer must be able to identify which engine produced an assessment and inspect the evidence and limitations behind it.

Where competing assessment engines produce different results, PKL should preserve the competing assessments rather than silently treating one as objectively correct.

## 14. Open questions

The following remain deliberately unresolved and require testing before v1.0:

- exact reputation mathematics;
- exact aggregation of Evidence Profile dimensions;
- governance and rule-change procedure;
- cryptographic identity design;
- database schema and API contract;
- privacy and redaction rules;
- abuse resistance and Sybil resistance;
- dispute resolution when reviewers remain divided;
- how competing assessment engines are identified, versioned, and compared;
- which Evidence Profile dimensions each assessment engine is permitted or required to use.
