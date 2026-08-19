# Public Knowledge Ledger — Project Plan

## 1. Purpose

Public Knowledge Ledger (PKL) is an open-source, auditable system for representing claims, evidence, provenance, disagreement, and review over time.

The goal is not to create a single authority that declares what is true. The goal is to make the basis for a knowledge assessment inspectable: what was claimed, what evidence was supplied, where that evidence came from, how independent it is, what contradicts it, and how the assessment changed.

## 2. Project principles

- **Evidence is not repetition.** Multiple reports derived from one underlying source should not automatically count as independent support.
- **Provenance matters.** The origin and relationships of evidence must be represented explicitly.
- **Disagreement is preserved.** Contradictory evidence is part of the record, not something to hide or overwrite.
- **History is auditable.** Important changes should be represented as ledger events and remain replayable.
- **Assessments are explainable.** PKL should expose why an assessment exists rather than reducing epistemic quality to an opaque score.
- **Uncertainty is explicit.** Unknown, disputed, weakly supported, and well-supported claims should remain distinguishable.
- **No single authority determines truth.** Review and council mechanisms should support accountable judgement without becoming an unquestionable oracle.

## 3. Current state

PKL has moved beyond a basic prototype and now has a working security/audit foundation plus first-class evidence and provenance support.

### Completed

- Append-only ledger foundation.
- Cryptographic integrity/authentication mechanisms.
- Replay and auditability.
- Council/quorum mechanisms.
- Claim and evidence foundations.
- Evidence Profile with independently represented dimensions on a 0–5 ordinal scale.
- Audited Evidence Profile updates.
- Provenance graph integrated with the ledger.
- Replayable provenance links.
- Provenance-aware independence hints.
- Snapshot/serialization support for evidence profiles and provenance.
- End-to-end tests covering derived reporting, independent evidence, replay, and snapshots.
- Automated CI running the full test suite.

## 4. V1 definition of done

PKL v1 is complete when a user can:

1. Submit a claim.
2. Attach structured evidence to that claim.
3. Record the provenance of that evidence.
4. Distinguish independent evidence from derivative reporting.
5. Represent evidence that supports and contradicts a claim.
6. Produce an explicit, explainable assessment from the available evidence and review process.
7. Change that assessment when new evidence arrives without erasing the historical record.
8. Replay the ledger and independently verify the resulting state.
9. Query the resulting knowledge state and inspect its supporting evidence, contradictions, provenance, and history.
10. Run the system from documented, reproducible source with automated tests passing.

V1 does **not** require every open research question to have a mathematically final answer. Where the model remains provisional, that uncertainty should be explicit and documented.

## 5. Milestones

| Milestone | Goal | Status |
|---|---|---|
| M0 | Core ledger, integrity, authentication, replay, and council foundations | Complete |
| M1 | Evidence Profiles and provenance-aware independence | Complete |
| M2 | Claim assessment from supporting/contradicting evidence | Next |
| M3 | Disputes, corrections, and assessment history | Planned |
| M4 | Practical source/evidence ingestion | Planned |
| M5 | Query/API layer for inspecting claims and evidence | Planned |
| M6 | Privacy, redaction, abuse resistance, and Sybil considerations | Planned |
| M7 | Real-world validation and external adversarial review | Planned |
| M8 | Public v1 release | Planned |

## 6. Immediate priority — M2: Claim assessment

Build the smallest complete vertical slice that answers:

> What evidence supports this claim, what independently contradicts it, and why is the current assessment what it is?

The implementation should include:

- explicit support/contradiction relationships;
- provenance-family awareness when considering independence;
- an explainable assessment state;
- preservation of contradictory evidence;
- deterministic/replayable assessment behaviour where practical;
- end-to-end fixtures demonstrating convergence, derivative reporting, contradiction, and change over time.

Avoid introducing an opaque single-number confidence score as a shortcut. The existing Evidence Profile dimensions should remain inspectable individually.

## 7. M3: Disputes and corrections

Once claim assessment exists, add first-class handling for:

- challenges to an existing assessment;
- new evidence that changes an assessment;
- corrections to previously recorded information;
- reviewer/council disagreement;
- historical comparison of assessments;
- explicit resolution and unresolved states.

The key requirement is that correction must add to the history rather than rewrite it.

## 8. M4: Practical ingestion

Provide a clear path from a real source to structured evidence and claims.

Initial scope should remain deliberately small. The first ingestion path should establish:

```text
Source → Evidence → Provenance → Claim → Assessment
```

Potential inputs can include URLs and manually supplied source metadata before attempting broad automated extraction.

## 9. M5: Query/API layer

Make the ledger useful to someone who did not write the Python internals.

The first API/query surface should make it possible to inspect:

- a claim and current assessment;
- supporting evidence;
- contradicting evidence;
- provenance relationships;
- independence groupings;
- Evidence Profiles;
- assessment history;
- ledger/audit history.

The API should expose uncertainty and provenance rather than hiding them behind a simplified verdict.

## 10. M6: Trust, privacy, and abuse resistance

Before public deployment, address the security and governance questions that are not solved by cryptographic integrity alone:

- reviewer reputation;
- Sybil resistance;
- collusion/manipulation resistance;
- privacy and redaction;
- sensitive source handling;
- abuse/reporting mechanisms;
- permissions and contributor identity;
- limits of automated assessment.

These should be treated as design/research problems and tested explicitly rather than assumed away.

## 11. M7: Real-world validation

Use a small, carefully selected set of real claims to test whether the model is useful outside synthetic fixtures.

Target roughly 10–20 cases spanning:

- strong independent convergence;
- derivative reporting;
- genuine disagreement;
- changing evidence;
- ambiguous or incomplete provenance;
- claims for which the evidence quality is mixed.

Record where the model fails or produces unintuitive results. These cases should drive revisions to the specification and tests.

## 12. External review and key stakeholders

Once M2–M7 produce a credible demonstration, seek adversarial feedback from:

1. epistemology / evidence researchers;
2. open-source and knowledge-graph communities;
3. researchers and data publishers;
4. public-sector or other authoritative information producers;
5. journalists or fact-checking practitioners where appropriate.

The preferred initial request is not adoption. It is critique:

> We have built a small open-source prototype for representing claims, evidence, provenance and disagreement in an auditable way. Could you try to break the model and tell us where it fails?

Feedback should become issues, tests, and specification changes where appropriate.

## 13. Not yet

To protect the core project from premature complexity, the following are explicitly out of scope until the underlying model has earned them:

- a large web frontend;
- token/cryptocurrency economics;
- blockchain integration for its own sake;
- an opaque AI truth/confidence score;
- large-scale automated web crawling;
- elaborate governance machinery before real-world validation;
- production-scale infrastructure before the data model and assessment behaviour are stable.

These may become useful later, but they should not displace the core evidence/provenance work.

## 14. Quality gates

A milestone should not be considered complete merely because its code exists. Each milestone should aim to leave behind:

- automated tests;
- an end-to-end example where appropriate;
- replay/audit coverage for state-changing behaviour;
- documentation of important design decisions;
- explicit treatment of failure and uncertainty;
- green CI.

For externally meaningful milestones, add adversarial or real-world cases rather than relying solely on unit tests.

## 15. Working rule

Prefer **small, complete vertical slices** over large infrastructure projects.

When choosing between two possible next tasks, favour the one that moves PKL closer to answering this question convincingly:

> **Can an independent observer inspect a claim, its evidence, its provenance, its contradictions, and its history, and understand why PKL currently represents it the way it does?**

That is the core product. Everything else supports it.
