from pkl.provenance import ProvenanceGraph


def test_transitive_chain_is_one_dependency_family():
    graph = ProvenanceGraph()
    graph.add("ORIGINAL", "A", "derived_from")
    graph.add("A", "B", "cites")
    graph.add("B", "C", "derived_from")

    assert graph.provenance_family("ORIGINAL") == {"ORIGINAL", "A", "B", "C"}
    assert graph.independence_hint("ORIGINAL", "C") == "not_independent_or_requires_review"


def test_disconnected_evidence_is_not_assumed_independent():
    graph = ProvenanceGraph()

    assert graph.independence_hint("A", "B") == "unknown"


def test_independent_research_can_share_claim_without_dependency():
    graph = ProvenanceGraph()
    graph.add("A", "B", "independent_of", "Different investigators and datasets")

    assert graph.independence_hint("A", "B") == "potentially_independent"
    assert graph.provenance_family("A") == {"A"}
    assert graph.provenance_family("B") == {"B"}
