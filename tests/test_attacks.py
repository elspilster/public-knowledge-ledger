import pytest

from pkl.auth import generate_signer, sign_event
from pkl.delegation import SignedDelegation
from pkl.ledger import Ledger
from pkl.root_of_trust import Authority, RootOfTrust


def test_tampered_delegation_key_is_rejected():
    root = generate_signer("root")
    delegate = generate_signer("delegate")
    forged_key = generate_signer("attacker").public_key
    event_id = "EVT-DELEGATE-1"
    previous_hash = "0" * 64
    payload = {"authority_id": "root", "delegate_id": "delegate", "delegate_public_key": delegate.public_key.hex()}
    signature = sign_event(root, event_id, "authority.delegated", "delegate", event_id, payload, previous_hash)
    delegation = SignedDelegation(event_id, "root", "delegate", forged_key, signature, previous_hash)
    trust = RootOfTrust(Authority("root", root.public_key))
    with pytest.raises(ValueError, match="Invalid delegation signature"):
        trust.add_delegation(delegation)


def test_ledger_does_not_accept_evidence_for_unknown_claim():
    ledger = Ledger()
    with pytest.raises(KeyError):
        ledger.add_evidence("PKL-does-not-exist", "fake", "fake")


def test_ledger_rejects_unknown_counter_evidence():
    ledger = Ledger()
    claim = ledger.create_claim("test")
    with pytest.raises(KeyError):
        ledger.challenge_claim(claim.id, "counter", counter_evidence_ids=["EVD-fake"])


def test_tampering_with_audit_history_is_detected():
    ledger = Ledger()
    claim = ledger.create_claim("original")
    ledger.add_evidence(claim.id, "source", "description")
    assert ledger.verify() is True
    ledger.events[0].payload["text"] = "tampered"
    assert ledger.verify() is False
