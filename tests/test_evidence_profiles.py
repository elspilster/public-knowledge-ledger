import pytest

from pkl import EvidenceProfile, Ledger
from pkl.serialization import export_ledger, import_ledger


def test_evidence_profile_keeps_dimensions_separate():
    profile = EvidenceProfile(
        methodology_quality=5,
        source_quality=4,
        independence=3,
        replication=2,
        sample_data_strength=5,
        bias_risk=1,
        transparency=4,
        predictive_success=3,
        contradictory_evidence=0,
        relevance=5,
        independence_level="I3",
    )
    profile.validate()

    assert profile.as_dict()["methodology_quality"] == 5
    assert profile.as_dict()["bias_risk"] == 1
    assert profile.as_dict()["independence_level"] == "I3"


def test_invalid_profile_dimension_is_rejected():
    with pytest.raises(ValueError):
        EvidenceProfile(source_quality=6).validate()

    with pytest.raises(ValueError):
        EvidenceProfile(independence_level="I9").validate()


def test_profile_update_is_audited_and_replayable():
    ledger = Ledger()
    claim = ledger.create_claim("Independent studies converge on the result.")
    evidence = ledger.add_evidence(claim.id, "Study A", "Primary study", source="study-a")

    ledger.update_evidence_profile(
        evidence.id,
        EvidenceProfile(methodology_quality=5, source_quality=5, relevance=5, independence_level="I3"),
    )

    assert ledger.evidence[evidence.id].profile.methodology_quality == 5
    assert ledger.history(evidence.id)[-1].event_type == "evidence.profile_updated"
    assert ledger.verify()


def test_provenance_prevents_counting_derived_reporting_as_independent():
    ledger = Ledger()
    claim = ledger.create_claim("A claim with multiple reports.")
    original = ledger.add_evidence(claim.id, "Original study", "Primary research", source="study-a")
    report_a = ledger.add_evidence(claim.id, "Report A", "Reports the original study", source="report-a")
    report_b = ledger.add_evidence(claim.id, "Report B", "Reports Report A", source="report-b")
    independent = ledger.add_evidence(claim.id, "Independent study", "Separate research", source="study-b")

    ledger.link_evidence(report_a.id, original.id, "derived_from")
    ledger.link_evidence(report_b.id, report_a.id, "derived_from")

    assert ledger.evidence_independence(report_a.id, original.id) == "not_independent_or_requires_review"
    assert ledger.evidence_independence(report_b.id, original.id) == "not_independent_or_requires_review"
    assert ledger.evidence_independence(independent.id, original.id) == "unknown"
    assert ledger.provenance.provenance_family(report_b.id) == {report_b.id, report_a.id, original.id}
    assert ledger.verify()


def test_profile_and_provenance_survive_snapshot_round_trip():
    ledger = Ledger()
    claim = ledger.create_claim("Snapshot test")
    first = ledger.add_evidence(claim.id, "Primary", "Primary evidence")
    second = ledger.add_evidence(claim.id, "Derivative", "Derivative evidence")
    ledger.update_evidence_profile(second.id, EvidenceProfile(methodology_quality=4, independence_level="I1"))
    ledger.link_evidence(second.id, first.id, "derived_from", "Cites the primary source")

    restored = import_ledger(export_ledger(ledger))

    assert restored.evidence[second.id].profile.independence_level == "I1"
    assert restored.provenance.edges[0].relation == "derived_from"
    assert restored.evidence_independence(second.id, first.id) == "not_independent_or_requires_review"
    assert restored.verify()
