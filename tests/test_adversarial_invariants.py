import copy

import pytest

from pkl.ledger import Ledger


def test_event_deletion_is_detected():
    ledger = Ledger()
    ledger.create_claim("claim")
    ledger.add_evidence(next(iter(ledger.claims)), "source", "evidence")
    assert ledger.verify()
    ledger.events.pop()
    assert not ledger.verify()


def test_event_insertion_is_detected():
    ledger = Ledger()
    ledger.create_claim("claim")
    assert ledger.verify()
    forged = copy.deepcopy(ledger.events[0])
    forged.id = "EVT-FORGED"
    ledger.events.append(forged)
    assert not ledger.verify()


def test_event_reordering_is_detected():
    ledger = Ledger()
    claim = ledger.create_claim("claim")
    ledger.add_evidence(claim.id, "source", "evidence")
    assert ledger.verify()
    ledger.events.reverse()
    assert not ledger.verify()


def test_unknown_event_type_cannot_replay():
    ledger = Ledger()
    ledger.create_claim("claim")
    event = ledger.events[0]
    event.event_type = "root.magic_override"
    assert not ledger.verify()


def test_empty_claim_is_rejected():
    ledger = Ledger()
    with pytest.raises(ValueError):
        ledger.create_claim("   ")


def test_evidence_cannot_move_between_claims_without_detection():
    ledger = Ledger()
    first = ledger.create_claim("first")
    second = ledger.create_claim("second")
    evidence = ledger.add_evidence(first.id, "source", "evidence")
    assert ledger.verify()
    evidence.claim_id = second.id
    assert not ledger.verify()


def test_assessment_tampering_is_detected():
    ledger = Ledger()
    claim = ledger.create_claim("claim")
    ledger.assess_claim(claim.id, "supported", evidence_level="E3", summary="supported")
    assert ledger.verify()
    claim.status = "rejected"
    assert not ledger.verify()
