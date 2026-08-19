import pytest

from pkl import Ledger


def test_create_claim_records_history():
    ledger = Ledger()
    claim = ledger.create_claim("Earth is approximately spherical.", contributor_id="SKL-HUMAN-0001")

    assert claim.id.startswith("PKL-")
    assert ledger.get_claim(claim.id).text == "Earth is approximately spherical."
    assert ledger.history(claim.id)[0].event_type == "claim.created"


def test_evidence_is_attached_to_claim():
    ledger = Ledger()
    claim = ledger.create_claim("Water contains hydrogen and oxygen.")
    evidence = ledger.add_evidence(
        claim.id,
        "Independent observation",
        "An observation supporting the claim.",
        supports_claim=True,
    )

    assert evidence.id in claim.evidence_ids
    assert ledger.evidence[evidence.id].claim_id == claim.id


def test_unknown_claim_is_rejected():
    ledger = Ledger()
    with pytest.raises(KeyError):
        ledger.add_evidence("PKL-does-not-exist", "Evidence", "Description")


def test_challenge_is_preserved():
    ledger = Ledger()
    claim = ledger.create_claim("Test claim")
    challenge = ledger.challenge_claim(claim.id, "This claim needs stronger evidence.")

    assert challenge.id in claim.challenge_ids
    assert challenge.status == "open"
    assert ledger.history(challenge.id)[0].event_type == "challenge.created"


def test_assessment_changes_current_state_without_erasing_history():
    ledger = Ledger()
    claim = ledger.create_claim("Test claim")
    ledger.assess_claim(claim.id, "uncertain", evidence_level="E2", summary="Evidence is limited.")
    ledger.assess_claim(claim.id, "supported", evidence_level="E3", summary="Independent support found.")

    assert claim.status == "supported"
    events = ledger.history(claim.id)
    assert [event.event_type for event in events] == [
        "claim.created",
        "claim.assessed",
        "claim.assessed",
    ]


def test_invalid_evidence_level_is_rejected():
    ledger = Ledger()
    claim = ledger.create_claim("Test claim")
    with pytest.raises(ValueError):
        ledger.assess_claim(claim.id, "supported", evidence_level="E9")
