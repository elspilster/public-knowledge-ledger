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

    def independence_hint(self, first_id: str, second_id: str) -> str:
        """Return a conservative hint; final independence requires review.

        Direct duplication, citation, shared datasets, or shared experiments
        are evidence against treating two items as independent. An explicit
        independent_of relation is evidence in favour, but is not by itself
        proof.
        """
        relation = self.direct_relation(first_id, second_id)
        if relation in {"duplicates", "cites", "same_dataset", "same_experiment", "derived_from"}:
            return "not_independent_or_requires_review"
        if relation == "independent_of":
            return "potentially_independent"
        if relation == "reproduces":
            return "independent_status_requires_review"
        return "unknown"
