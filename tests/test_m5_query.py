from pkl import KnowledgeQuery, Ledger


def test_query_exposes_contradictions_history_and_reviews():
    ledger = Ledger()
    claim = ledger.create_claim("A claim")
    supporting = ledger.add_evidence(claim.id, "Support", "Supporting evidence", supports_claim=True)
    contradicting = ledger.add_evidence(claim.id, "Contradiction", "Contradicting evidence", supports_claim=False)
    ledger.assess_claim(claim.id, "disputed", evidence_level="E1", summary="Evidence conflicts")
    review = ledger.review_assessment(claim.id, "reviewer", "uncertain", rationale="The conflict remains material")

    result = KnowledgeQuery(ledger).explain(claim.id)
    assert {item["id"] for item in result["evidence"]} == {supporting.id, contradicting.id}
    assert result["claim"]["status"] == "disputed"
    assert result["assessment_history"][0]["status"] == "disputed"
    assert result["reviews"][0]["id"] == review.id
    assert result["authenticated_is_not_true"] is True


def test_query_uses_ledger_provenance_by_default():
    ledger = Ledger()
    claim = ledger.create_claim("A claim")
    first = ledger.add_evidence(claim.id, "First", "First evidence")
    second = ledger.add_evidence(claim.id, "Second", "Second evidence")
    ledger.link_evidence(second.id, first.id, "derived_from")

    result = KnowledgeQuery(ledger).explain(claim.id)
    evidence = {item["id"]: item for item in result["evidence"]}
    assert evidence[second.id]["provenance"]
    assert evidence[second.id]["provenance"][0]["relation"] == "derived_from"
