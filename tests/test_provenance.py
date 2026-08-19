import pytest

from pkl.provenance import ProvenanceGraph


def test_copies_are_not_counted_as_independent():
    graph = ProvenanceGraph()
    graph.add("EVD-A", "EVD-B", "duplicates")

    assert graph.independence_hint("EVD-A", "EVD-B") == "not_independent_or_requires_review"


def test_shared_dataset_requires_review():
    graph = ProvenanceGraph()
    graph.add("EVD-A", "EVD-B", "same_dataset")

    assert graph.independence_hint("EVD-A", "EVD-B") == "not_independent_or_requires_review"


def test_explicit_independence_is_only_a_positive_hint():
    graph = ProvenanceGraph()
    graph.add("EVD-A", "EVD-B", "independent_of", "Different investigators and datasets")

    assert graph.independence_hint("EVD-A", "EVD-B") == "potentially_independent"


def test_unknown_relationship_is_not_assumed_independent():
    graph = ProvenanceGraph()

    assert graph.independence_hint("EVD-A", "EVD-B") == "unknown"


def test_self_relation_is_rejected():
    graph = ProvenanceGraph()
    with pytest.raises(ValueError):
        graph.add("EVD-A", "EVD-A", "cites")
