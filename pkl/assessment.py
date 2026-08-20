"""Explainable claim assessment for PKL.

The assessor derives a bounded evidence status from recorded evidence. It does
not claim to establish metaphysical truth or prove epistemic independence.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .models import Assessment, Claim, Evidence
from .provenance import ProvenanceGraph


AssessmentStatus = Literal["supported", "disputed", "uncertain", "insufficient_evidence"]


@dataclass(frozen=True)
class AssessmentResult:
    status: AssessmentStatus
    evidence_level: str
    summary: str
    supporting_ids: tuple[str, ...]
    contradicting_ids: tuple[str, ...]
    provenance_notes: tuple[str, ...]
    limitations: tuple[str, ...]


def assess_claim(
    claim: Claim,
    evidence: dict[str, Evidence],
    provenance: ProvenanceGraph,
) -> AssessmentResult:
    items = [evidence[eid] for eid in claim.evidence_ids if eid in evidence]
    supporting = [item for item in items if item.supports_claim is True]
    contradicting = [item for item in items if item.supports_claim is False]

    if not items:
        return AssessmentResult(
            "insufficient_evidence", "E0", "No evidence is recorded for this claim.", (), (), (),
            ("The ledger cannot assess evidence that has not been submitted.",),
        )

    support_strength = _independent_family_count(supporting, provenance)
    contradiction_strength = _independent_family_count(contradicting, provenance)
    limitations: list[str] = []
    provenance_notes: list[str] = []

    if support_strength == 0 and contradicting:
        status: AssessmentStatus = "disputed"
    elif support_strength > contradiction_strength and support_strength >= 2:
        status = "supported"
    elif contradiction_strength > support_strength and contradiction_strength >= 2:
        status = "disputed"
    elif supporting and contradicting:
        status = "disputed"
    elif supporting:
        status = "supported"
    else:
        status = "uncertain"

    for item in items:
        if item.profile.provenance_distinctness in {"I3", "I4"} or item.profile.independence_level in {"I3", "I4"}:
            provenance_notes.append(
                f"{item.id}: high recorded provenance distinctness does not establish absence of hidden shared bias."
            )
        metadata = item.metadata
        if metadata.get("known_correlations") or metadata.get("conflicts_of_interest"):
            limitations.append(f"{item.id}: known correlation or conflict metadata is present.")
        if metadata.get("unknown_dependencies"):
            limitations.append(f"{item.id}: external dependencies remain unknown.")

    if not contradicting:
        limitations.append("No contradiction is recorded; absence of a recorded contradiction is not proof that none exists.")

    level = _evidence_level(support_strength, contradiction_strength, len(items))
    summary = (
        f"Assessment is {status} from {len(supporting)} supporting and {len(contradicting)} "
        f"contradicting evidence items, representing {support_strength} and {contradiction_strength} "
        "recorded provenance families respectively."
    )
    return AssessmentResult(
        status, level, summary, tuple(item.id for item in supporting),
        tuple(item.id for item in contradicting), tuple(dict.fromkeys(provenance_notes)),
        tuple(dict.fromkeys(limitations)),
    )


def _independent_family_count(items: list[Evidence], provenance: ProvenanceGraph) -> int:
    families: list[set[str]] = []
    for item in items:
        family = provenance.provenance_family(item.id)
        if not any(family & existing for existing in families):
            families.append(family)
    return len(families)


def _evidence_level(support: int, contradiction: int, total: int) -> str:
    if total == 0:
        return "E0"
    if support >= 3 and contradiction == 0:
        return "E4"
    if support >= 2 and contradiction == 0:
        return "E3"
    if support >= 1 and contradiction == 0:
        return "E2"
    if support > 0 or contradiction > 0:
        return "E1"
    return "E0"
