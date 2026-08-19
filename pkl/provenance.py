"""Provenance graph for tracing evidence relationships and independence.

The graph records relationships; it does not pretend that graph structure
alone proves independence. Independence is an assessment that can be updated
as provenance becomes better understood.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


Relation = Literal[
    "derived_from",
    "cites",
    "duplicates",
    "reproduces",
    "independent_of",
    "same_dataset",
    "same_experiment",
]

DEPENDENCY_RELATIONS = {
    "derived_from",
    "cites",
    "duplicates",
    "same_dataset",
    "same_experiment",
}


@dataclass(frozen=True)
class ProvenanceEdge:
    source_id: str
    target_id: str
    relation: Relation
    note: str = ""


@dataclass
class ProvenanceGraph:
    edges: list[ProvenanceEdge] = field(default_factory=list)

    def add(self, source_id: str, target_id: str, relation: Relation, note: str = "") -> ProvenanceEdge:
        if source_id == target_id:
            raise ValueError("An evidence item cannot be related to itself")
        edge = ProvenanceEdge(source_id, target_id, relation, note)
        if edge not in self.edges:
            self.edges.append(edge)
        return edge

    def related(self, evidence_id: str) -> list[ProvenanceEdge]:
        return [
            edge for edge in self.edges
            if edge.source_id == evidence_id or edge.target_id == evidence_id
        ]

    def direct_relation(self, first_id: str, second_id: str) -> Relation | None:
        for edge in self.edges:
            if (edge.source_id, edge.target_id) == (first_id, second_id):
                return edge.relation
            if (edge.source_id, edge.target_id) == (second_id, first_id):
                return edge.relation
        return None

    def _reachable_via_dependency(self, start_id: str) -> set[str]:
        """Return nodes connected to start through dependency-like edges.

        This is deliberately conservative: a provenance connection is enough
        to flag a relationship for review, but it does not by itself prove
        that two observations are scientifically non-independent.
        """
        seen = {start_id}
        stack = [start_id]
        while stack:
            current = stack.pop()
            for edge in self.edges:
                if edge.relation not in DEPENDENCY_RELATIONS:
                    continue
                neighbour = None
                if edge.source_id == current:
                    neighbour = edge.target_id
                elif edge.target_id == current:
                    neighbour = edge.source_id
                if neighbour is not None and neighbour not in seen:
                    seen.add(neighbour)
                    stack.append(neighbour)
        return seen

    def provenance_family(self, evidence_id: str) -> set[str]:
        """Return the conservative dependency family containing an item."""
        return self._reachable_via_dependency(evidence_id)

    def independence_hint(self, first_id: str, second_id: str) -> str:
        """Return a conservative hint; final independence requires review.

        Direct duplication, citation, shared datasets, shared experiments, or
        derived provenance are evidence against treating two items as
        independent. An explicit independent_of relation is evidence in
        favour, but is not by itself proof.
        """
        relation = self.direct_relation(first_id, second_id)
        if relation in DEPENDENCY_RELATIONS:
            return "not_independent_or_requires_review"
        if relation == "independent_of":
            return "potentially_independent"
        if relation == "reproduces":
            return "independent_status_requires_review"

        first_family = self.provenance_family(first_id)
        second_family = self.provenance_family(second_id)
        if first_id in second_family or second_id in first_family:
            return "not_independent_or_requires_review"
        return "unknown"
