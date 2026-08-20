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


def test_claim_relationship_duplicate_is_rejected():
    ledger = Ledger()
    first = ledger.create_claim("Claim A")
    second = ledger.create_claim("Claim B")

    ledger.relate_claims(first.id, second.id, "semantically_related")

    with pytest.raises(ValueError, match="already exists"):
        ledger.relate_claims(first.id, second.id, "semantically_related")


def test_claim_relationship_cycle_is_rejected():
    ledger = Ledger()
    first = ledger.create_claim("Claim A")
    second = ledger.create_claim("Claim B")
    third = ledger.create_claim("Claim C")

    ledger.relate_claims(first.id, second.id, "narrower_than")
    ledger.relate_claims(second.id, third.id, "broader_than")

    with pytest.raises(ValueError, match="cannot create cycles"):
        ledger.relate_claims(third.id, first.id, "semantically_related")


def test_rejected_claim_relationship_does_not_change_state_or_history():
    ledger = Ledger()
    first = ledger.create_claim("Claim A")
    second = ledger.create_claim("Claim B")
    ledger.relate_claims(first.id, second.id, "duplicate_of")
    event_count = len(ledger.events)

    with pytest.raises(ValueError):
        ledger.relate_claims(second.id, first.id, "duplicate_of")

    assert ledger.claims[second.id].related_claim_ids == []
    assert len(ledger.events) == event_count
    assert ledger.verify()
