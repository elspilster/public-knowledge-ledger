"""Explainable claim assessment for PKL.

The assessor derives a bounded evidence status from recorded evidence. It does
not claim to establish metaphysical truth or prove epistemic independence.

This first assessment engine is intentionally narrow: it counts distinct
recorded provenance families and applies explicitly documented safeguards for
known correlations. Evidence Profile quality dimensions are *not* silently
converted into a score here; a future engine may use them explicitly and must
identify its rule/version when doing so.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .models import Claim, Evidence
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

    support_strength, support_correlations = _family_count_with_correlations(supporting, provenance)
    contradiction_strength, contradiction_correlations = _family_count_with_correlations(contradicting, provenance)
    limitations: list[str] = []
    provenance_notes: list[str] = []

    if support_correlations:
        limitations.append(
            "Supporting evidence sharing declared correlation/COI tags was counted as one recorded evidence family."
        )
    if contradiction_correlations:
        limitations.append(
            "Contradicting evidence sharing declared correlation/COI tags was counted as one recorded evidence family."
        )

    if support_strength == 0 and contradicting:
        status: AssessmentStatus = "disputed"
    elif support_strength > contradiction_strength and support_strength >= 2:
        status = "supported"
    elif contradiction_strength > support_strength and contradiction_strength >= 2:
        status = "disputed"
    elif supporting and contradicting:
        status = "disputed"
    else:
        status = "uncertain"

    for item in items:
        if item.profile.provenance_distinctness in {"I3", "I4"} or item.profile.independence_level in {"I3", "I4"}:
            provenance_notes.append(
                f"{item.id}: high recorded provenance distinctness does not establish absence of hidden shared bias."
            )
        metadata = item.metadata
        if metadata.get("known_correlations") or metadata.get("conflicts_of_interest"):
            limitations.append(f"{item.id}: known correlation or conflict metadata is present and affects family counting.")
        if metadata.get("unknown_dependencies"):
            limitations.append(f"{item.id}: external dependencies remain unknown.")

    if supporting and contradicting:
        limitations.append(
            "Supporting and contradicting evidence are both recorded; this assessment does not resolve the underlying disagreement."
        )
    elif not contradicting:
        limitations.append("No contradiction is recorded; absence of a recorded contradiction is not proof that none exists.")

    level = _evidence_level(support_strength, contradiction_strength, len(items), limitations)
    summary = (
        f"Assessment is {status} from {len(supporting)} supporting and {len(contradicting)} "
        f"contradicting evidence items, representing {support_strength} and {contradiction_strength} "
        "recorded provenance families respectively. This engine does not infer epistemic independence."
    )
    return AssessmentResult(
        status, level, summary, tuple(item.id for item in supporting),
        tuple(item.id for item in contradicting), tuple(dict.fromkeys(provenance_notes)),
        tuple(dict.fromkeys(limitations)),
    )


def _correlation_keys(item: Evidence) -> set[str]:
    """Return explicit dependency/correlation labels for one evidence item."""
    metadata = item.metadata
    keys: set[str] = set()
    for field in ("known_correlations", "conflicts_of_interest"):
        values = metadata.get(field, ())
        if isinstance(values, str):
            values = (values,)
        if isinstance(values, (list, tuple, set, frozenset)):
            keys.update(f"{field}:{value}" for value in values if value)
    return keys


def _family_count_with_correlations(
    items: list[Evidence], provenance: ProvenanceGraph
) -> tuple[int, set[str]]:
    """Count connected provenance families, merging explicit shared-risk tags."""
    groups: list[set[str]] = []
    group_keys: list[set[str]] = []
    correlations: set[str] = set()

    for item in items:
        family = set(provenance.provenance_family(item.id)) & {candidate.id for candidate in items}
        family.add(item.id)
        keys = _correlation_keys(item)
        correlations.update(keys)

        overlapping = [
            index for index, existing in enumerate(groups)
            if existing & family or group_keys[index] & keys
        ]
        if not overlapping:
            groups.append(family)
            group_keys.append(keys)
            continue

        merged_group = set(family)
        merged_keys = set(keys)
        for index in reversed(overlapping):
            merged_group.update(groups.pop(index))
            merged_keys.update(group_keys.pop(index))
        groups.append(merged_group)
        group_keys.append(merged_keys)

    return len(groups), correlations


def _independent_family_count(items: list[Evidence], provenance: ProvenanceGraph) -> int:
    """Backward-compatible family count helper used by older callers/tests."""
    return _family_count_with_correlations(items, provenance)[0]


def _evidence_level(support: int, contradiction: int, total: int, limitations: list[str]) -> str:
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
