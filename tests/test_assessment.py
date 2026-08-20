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


def test_assessment_exposes_hidden_dependency_limitations_without_claiming_independence():
    ledger = Ledger()
    claim = ledger.create_claim("A claim with a disclosed correlation")
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
    )
    result = ledger.assess_claim_from_evidence(claim.id)

    assert result.status == "supported"
    assert any(first.id in limitation and "correlation" in limitation for limitation in result.limitations)
    assert any(first.id in note and "does not establish" in note for note in result.provenance_notes)
    assert second.id in result.supporting_evidence_ids


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
    assert "No evidence" in assessed.assessment.summary
    assert ledger.history(claim.id)[-1].event_type == "claim.assessed"
