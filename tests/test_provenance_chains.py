from pkl.provenance import ProvenanceGraph


def test_derivative_chain_does_not_become_independent_by_repetition():
    graph = ProvenanceGraph()
    graph.add("EVD-A", "EVD-B", "derived_from")
    graph.add("EVD-B", "EVD-C", "cites")
    graph.add("EVD-C", "EVD-D", "derived_from")

    # Direct links already identify dependency. A later implementation should
    # also traverse this chain so D is not counted as independent of A merely
    # because it is several publications away.
    assert graph.independence_hint("EVD-A", "EVD-B") == "not_independent_or_requires_review"
    assert graph.independence_hint("EVD-B", "EVD-C") == "not_independent_or_requires_review"


def test_independent_branches_remain_separate():
    graph = ProvenanceGraph()
    graph.add("ORIGINAL", "EVD-A", "derived_from")
    graph.add("ORIGINAL", "EVD-B", "derived_from")
    graph.add("EVD-A", "EVD-B", "independent_of", "Different investigators, but both traced to the same original source")

    # The graph must not silently promote a declared relationship to proof.
    assert graph.independence_hint("EVD-A", "EVD-B") == "potentially_independent"
