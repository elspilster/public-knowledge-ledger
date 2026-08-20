from pkl import EvidenceProfile, Ledger


def test_assessment_counts_recorded_provenance_families_not_reports():
    ledger = Ledger()
    claim = ledger.create_claim("A well-supported claim")
    original = ledger.add_evidence(claim.id, "Original", "Primary study", supports_claim=True)
    report = ledger.add_evidence(claim.id, "Report", "Reports the original", supports_claim=True)
    independent = ledger.add_evidence(claim.id, "Independent", "Separate study", supports_claim=True)
    ledger.link_evidence(report.id, original.id, "derived_from")

    result = ledger.assess_claim_from_evidence(claim.id)

    assert result.status == "supported"
    assert result.evidence_level == "E3"
    assert len(result.supporting_evidence_ids) == 3
    assert "provenance families" in result.summary


def test_disclosed_shared_correlation_is_load_bearing_for_family_counting():
    ledger = Ledger()
    claim = ledger.create_claim("A claim with correlated evidence")
    first = ledger.add_evidence(
        claim.id,
        "Study A",
        "Supporting study",
        supports_claim=True,
        profile=EvidenceProfile(provenance_distinctness="I4"),
        metadata={"known_correlations": ["shared_funder"]},
    )
    second = ledger.add_evidence(
        claim.id,
        "Study B",
        "Another supporting study",
        supports_claim=True,
        profile=EvidenceProfile(provenance_distinctness="I4"),
        metadata={"known_correlations": ["shared_funder"]},
    )

    result = ledger.assess_claim_from_evidence(claim.id)

    assert result.status == "uncertain"
    assert result.evidence_level == "E2"
    assert first.id in result.supporting_evidence_ids
    assert second.id in result.supporting_evidence_ids
    assert any("counted as one recorded evidence family" in limitation for limitation in result.limitations)


def test_shared_coi_overrides_apparent_provenance_distinctness():
    ledger = Ledger()
    claim = ledger.create_claim("A claim with apparently independent studies")
    first = ledger.add_evidence(
        claim.id,
        "Study A",
        "Different laboratory",
        source="journal-a",
        supports_claim=True,
        profile=EvidenceProfile(provenance_distinctness="I4"),
        metadata={"conflicts_of_interest": ["manufacturer-x"]},
    )
    second = ledger.add_evidence(
        claim.id,
        "Study B",
        "Different laboratory",
        source="journal-b",
        supports_claim=True,
        profile=EvidenceProfile(provenance_distinctness="I4"),
        metadata={"conflicts_of_interest": ["manufacturer-x"]},
    )

    result = ledger.assess_claim_from_evidence(claim.id)

    assert first.id in result.supporting_evidence_ids
    assert second.id in result.supporting_evidence_ids
    assert result.status == "uncertain"
    assert result.evidence_level == "E2"
    assert any("affects family counting" in limitation for limitation in result.limitations)


def test_conflicts_of_interest_are_load_bearing_for_family_counting():
    ledger = Ledger()
    claim = ledger.create_claim("A claim with shared conflict")
    ledger.add_evidence(
        claim.id,
        "Study A",
        "Supporting study",
        supports_claim=True,
        metadata={"conflicts_of_interest": ["manufacturer"]},
    )
    ledger.add_evidence(
        claim.id,
        "Study B",
        "Supporting study",
        supports_claim=True,
        metadata={"conflicts_of_interest": ["manufacturer"]},
    )

    result = ledger.assess_claim_from_evidence(claim.id)

    assert result.status == "uncertain"
    assert result.evidence_level == "E2"


def test_single_supporting_item_is_not_called_supported():
    ledger = Ledger()
    claim = ledger.create_claim("A claim with one supporting item")
    evidence = ledger.add_evidence(claim.id, "One study", "A single study", supports_claim=True)

    result = ledger.assess_claim_from_evidence(claim.id)

    assert result.status == "uncertain"
    assert result.evidence_level == "E2"
    assert evidence.id in result.supporting_evidence_ids


def test_hidden_dependency_remains_explicitly_unknown():
    ledger = Ledger()
    claim = ledger.create_claim("A claim with unknown dependencies")
    ledger.add_evidence(
        claim.id,
        "Study A",
        "Supporting study",
        supports_claim=True,
        metadata={"unknown_dependencies": ["funding_relationship"]},
    )
    ledger.add_evidence(claim.id, "Study B", "Another supporting study", supports_claim=True)

    result = ledger.assess_claim_from_evidence(claim.id)

    assert result.status == "supported"
    assert any("remain unknown" in limitation for limitation in result.limitations)


def test_transitive_family_merging_is_order_independent():
    ledger = Ledger()
    claim = ledger.create_claim("A bridged provenance family")
    first = ledger.add_evidence(claim.id, "A", "A", supports_claim=True)
    bridge = ledger.add_evidence(claim.id, "B", "B", supports_claim=True)
    last = ledger.add_evidence(claim.id, "C", "C", supports_claim=True)
    ledger.link_evidence(bridge.id, first.id, "derived_from")
    ledger.link_evidence(last.id, bridge.id, "derived_from")

    result = ledger.assess_claim_from_evidence(claim.id)

    assert result.status == "uncertain"
    assert result.evidence_level == "E2"


def test_contradictory_evidence_is_a_claim_relationship_not_a_profile_score():
    ledger = Ledger()
    claim = ledger.create_claim("A disputed claim")
    ledger.add_evidence(claim.id, "Support", "Supports", supports_claim=True)
    ledger.add_evidence(claim.id, "Counter", "Contradicts", supports_claim=False)

    result = ledger.assess_claim_from_evidence(claim.id)

    assert result.status == "disputed"
    assert result.contradicting_evidence_ids
    assert result.limitations


def test_no_evidence_is_explicitly_insufficient():
    ledger = Ledger()
    claim = ledger.create_claim("A claim without evidence")

    assessed = ledger.assess_claim_from_evidence(claim.id)

    assert assessed.status == "insufficient_evidence"
    assert assessed.evidence_level == "E0"
    assert "No evidence" in assessed.summary
    assert ledger.history(claim.id)[-1].event_type == "claim.assessed"
