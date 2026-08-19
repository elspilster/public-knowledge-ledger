import pytest

from pkl import KnowledgeQuery, Ledger, QuorumPolicy, RootCouncil, Seat
from pkl.provenance import ProvenanceGraph


def test_council_requires_quorum_and_records_decision():
    policy = QuorumPolicy(
        [Seat("a", "science"), Seat("b", "civil"), Seat("c", "industry"), Seat("d", "public")],
        threshold=4,
        min_categories=3,
    )
    council = RootCouncil(policy)
    with pytest.raises(ValueError, match="Quorum"):
        council.decide("claim-1", "accepted", {"a", "b", "c"}, "not enough signers")
    decision = council.decide("claim-1", "accepted", {"a", "b", "c", "d"}, "independent review supports acceptance")
    assert decision.target_id == "claim-1"
    assert council.latest("claim-1") == decision


def test_explain_claim_exposes_provenance_challenges_and_council():
    ledger = Ledger()
    claim = ledger.create_claim("Water boils at 100 C at standard pressure", "researcher-1")
    evidence = ledger.add_evidence(claim.id, "Reference measurement", "Controlled measurement", source="lab-a", contributor_id="researcher-2", supports_claim=True)
    challenge = ledger.challenge_claim(claim.id, "Check pressure assumptions", challenger_id="reviewer-1", counter_evidence_ids=[])
    ledger.assess_claim(claim.id, "supported", evidence_level="E3", summary="Supported by controlled measurement")

    provenance = ProvenanceGraph()
    provenance.add(evidence.id, "source-lab-a", "cites", "published measurement")
    council = RootCouncil(QuorumPolicy([Seat("a", "science"), Seat("b", "civil"), Seat("c", "industry"), Seat("d", "public")]))
    council.decide(claim.id, "accepted", {"a", "b", "c", "d"}, "quorum review")

    explanation = KnowledgeQuery(ledger, provenance, council).explain(claim.id)
    assert explanation["claim"]["status"] == "supported"
    assert explanation["evidence"][0]["id"] == evidence.id
    assert explanation["evidence"][0]["provenance"][0]["relation"] == "cites"
    assert explanation["challenges"][0]["id"] == challenge.id
    assert explanation["council"]["decision"] == "accepted"
    assert explanation["authenticated_is_not_true"] is True


def test_query_search_is_case_insensitive():
    ledger = Ledger()
    claim = ledger.create_claim("The public ledger is auditable")
    results = KnowledgeQuery(ledger).search("AUDITABLE")
    assert results == [{"id": claim.id, "text": claim.text, "status": "proposed"}]
