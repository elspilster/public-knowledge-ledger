import pytest

from pkl.audit import AuditChain
from pkl.auth import generate_signer, sign_event


def test_valid_signature_verifies():
    signer = generate_signer("human-1")
    chain = AuditChain()
    event = chain.append("EVT-1", "claim.created", "PKL-1", "2026-08-19T12:00:00+00:00", {"text": "Claim"})
    signature = sign_event(signer, event.event_id, event.event_type, event.object_id, event.timestamp, event.payload, event.previous_hash)
    chain.events[0] = type(event)(**{**event.__dict__, "signer_key_id": signer.key_id, "signature": signature})

    assert chain.verify() is True
    assert chain.verify_signatures({signer.key_id: signer.public_key}) is True


def test_modified_payload_invalidates_signature():
    signer = generate_signer("human-1")
    chain = AuditChain()
    event = chain.append("EVT-1", "claim.created", "PKL-1", "2026-08-19T12:00:00+00:00", {"text": "Claim"})
    signature = sign_event(signer, event.event_id, event.event_type, event.object_id, event.timestamp, event.payload, event.previous_hash)
    chain.events[0] = type(event)(**{**event.__dict__, "signer_key_id": signer.key_id, "signature": signature, "payload": {"text": "Forged"}})

    assert chain.verify_signatures({signer.key_id: signer.public_key}) is False


def test_wrong_key_is_rejected():
    signer = generate_signer("human-1")
    wrong = generate_signer("attacker")
    chain = AuditChain()
    event = chain.append("EVT-1", "claim.created", "PKL-1", "2026-08-19T12:00:00+00:00", {"text": "Claim"})
    signature = sign_event(signer, event.event_id, event.event_type, event.object_id, event.timestamp, event.payload, event.previous_hash)
    chain.events[0] = type(event)(**{**event.__dict__, "signer_key_id": signer.key_id, "signature": signature})

    assert chain.verify_signatures({signer.key_id: wrong.public_key}) is False


def test_unknown_signer_key_is_rejected():
    signer = generate_signer("human-1")
    chain = AuditChain()
    event = chain.append("EVT-1", "claim.created", "PKL-1", "2026-08-19T12:00:00+00:00", {"text": "Claim"})
    signature = sign_event(signer, event.event_id, event.event_type, event.object_id, event.timestamp, event.payload, event.previous_hash)
    chain.events[0] = type(event)(**{**event.__dict__, "signer_key_id": "unknown", "signature": signature})

    assert chain.verify_signatures({signer.key_id: signer.public_key}) is False


def test_malformed_signature_is_rejected():
    signer = generate_signer("human-1")
    chain = AuditChain()
    event = chain.append("EVT-1", "claim.created", "PKL-1", "2026-08-19T12:00:00+00:00", {"text": "Claim"})
    chain.events[0] = type(event)(**{**event.__dict__, "signer_key_id": signer.key_id, "signature": "not-a-signature"})

    assert chain.verify_signatures({signer.key_id: signer.public_key}) is False
