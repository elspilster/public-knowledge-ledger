import pytest

from pkl.provenance import ProvenanceGraph


def test_cycle_is_traversable_without_infinite_loop():
    graph = ProvenanceGraph()
    graph.add("A", "B", "derived_from")
    graph.add("B", "C", "cites")
    graph.add("C", "A", "derived_from")

    assert graph.provenance_family("A") == {"A", "B", "C"}
    assert graph.independence_hint("A", "C") == "not_independent_or_requires_review"


def test_conflicting_independence_and_dependency_is_not_silently_resolved():
    graph = ProvenanceGraph()
    graph.add("A", "B", "derived_from")
    graph.add("A", "B", "independent_of", "Conflicting claim requiring adjudication")

    assert graph.conflicting_relationships("A", "B") is True
    assert graph.independence_hint("A", "B") == "conflicting_provenance_requires_review"


def test_multiple_non_conflicting_relations_are_retained():
    graph = ProvenanceGraph()
    graph.add("A", "B", "reproduces")
    graph.add("A", "B", "independent_of")

    assert graph.direct_relations("A", "B") == {"reproduces", "independent_of"}
    assert graph.independence_hint("A", "B") == "potentially_independent"


def test_self_relation_remains_invalid():
    graph = ProvenanceGraph()
    with pytest.raises(ValueError):
        graph.add("A", "A", "derived_from")
