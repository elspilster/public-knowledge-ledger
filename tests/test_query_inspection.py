from pkl import KnowledgeQuery, Ledger


def test_query_exposes_contradictions_and_assessment_history():
    ledger = Ledger()
    claim = ledger.create_claim("A claim")
    supporting = ledger.add_evidence(claim.id, "Support", "Supporting evidence", supports_claim=True)
    contradicting = ledger.add_evidence(claim.id, "Contradiction", "Contradicting evidence", supports_claim=False)
    ledger.assess_claim(
        claim.id,
        "disputed",
        evidence_level="E1",
        summary="Both supporting and contradicting evidence are recorded.",
        supporting_evidence_ids=[supporting.id],
        contradicting_evidence_ids=[contradicting.id],
    )
    ledger.assess_claim(claim.id, "uncertain", evidence_level="E1", summary="The disagreement remains unresolved.")

    result = KnowledgeQuery(ledger).explain(claim.id)

    assert {item["id"] for item in result["evidence"]} == {supporting.id, contradicting.id}
    assert result["claim"]["status"] == "uncertain"
    assert len(result["history"]) >= 3
    assert result["authenticated_is_not_true"] is True


def test_query_uses_ledger_provenance_by_default():
    ledger = Ledger()
    claim = ledger.create_claim("A claim")
    first = ledger.add_evidence(claim.id, "First", "First evidence")
    second = ledger.add_evidence(claim.id, "Second", "Second evidence")
    ledger.add_provenance_edge(second.id, first.id, "derived_from")

    result = KnowledgeQuery(ledger).explain(claim.id)
    evidence = {item["id"]: item for item in result["evidence"]}

    assert evidence[second.id]["provenance"]
    assert evidence[second.id]["provenance"][0]["relation"] == "derived_from"
