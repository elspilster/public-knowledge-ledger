from dataclasses import replace

from pkl.audit import AuditChain
from pkl.auth import generate_signer, sign_event


TIMESTAMP = "2026-08-20T00:00:00+00:00"
PAYLOAD = {"text": "Claim"}


def signed_chain(signer):
    chain = AuditChain()
    event = chain.append("EVT-1", "claim.created", "PKL-1", TIMESTAMP, PAYLOAD)
    signature = sign_event(
        signer,
        event.event_id,
        event.event_type,
        event.object_id,
        event.timestamp,
        event.payload,
        event.previous_hash,
        signer_key_id=signer.key_id,
    )
    chain.events[0] = replace(event, signer_key_id=signer.key_id, signature=signature)
    return chain


def test_tampering_signer_key_id_breaks_audit_integrity():
    signer = generate_signer("human-1")
    chain = signed_chain(signer)
    chain.events[0] = replace(chain.events[0], signer_key_id="attacker:key")

    assert chain.verify() is False


def test_strict_signature_verification_rejects_unsigned_events():
    chain = AuditChain()
    chain.append("EVT-1", "claim.created", "PKL-1", TIMESTAMP, PAYLOAD)

    assert chain.verify_signatures({}, require_signatures=True) is False


def test_strict_signature_verification_accepts_valid_signed_event():
    signer = generate_signer("human-1")
    chain = signed_chain(signer)

    assert chain.verify_signatures({signer.key_id: signer.public_key}, require_signatures=True) is True


def test_signature_substitution_is_rejected():
    signer = generate_signer("human-1")
    attacker = generate_signer("attacker")
    chain = signed_chain(signer)
    attacker_signature = sign_event(
        attacker,
        chain.events[0].event_id,
        chain.events[0].event_type,
        chain.events[0].object_id,
        chain.events[0].timestamp,
        chain.events[0].payload,
        chain.events[0].previous_hash,
        signer_key_id=signer.key_id,
    )
    chain.events[0] = replace(chain.events[0], signature=attacker_signature)

    assert chain.verify() is True
    assert chain.verify_signatures({signer.key_id: signer.public_key}, require_signatures=True) is False


def test_signature_tampering_is_rejected():
    signer = generate_signer("human-1")
    chain = signed_chain(signer)
    chain.events[0] = replace(chain.events[0], signature="00" * 64)

    assert chain.verify() is True
    assert chain.verify_signatures({signer.key_id: signer.public_key}, require_signatures=True) is False


def test_registered_public_key_substitution_is_rejected():
    signer = generate_signer("human-1")
    attacker = generate_signer("attacker")
    chain = signed_chain(signer)

    assert chain.verify_signatures({signer.key_id: attacker.public_key}, require_signatures=True) is False
