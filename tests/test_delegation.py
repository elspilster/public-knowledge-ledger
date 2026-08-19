from pkl.auth import generate_signer, sign_event
from pkl.delegation import SignedDelegation, verify_delegation


def make_delegation(authority, delegate, event_id="EVT-1", previous_hash="0" * 64):
    payload = {"authority_id": authority.key_id, "delegate_id": delegate.key_id, "delegate_public_key": delegate.public_key.hex()}
    signature = sign_event(authority, event_id, "authority.delegated", delegate.key_id, event_id, payload, previous_hash)
    return SignedDelegation(event_id, authority.key_id, delegate.key_id, delegate.public_key, signature, previous_hash)


def test_valid_delegation_verifies():
    root = generate_signer("root")
    delegate = generate_signer("delegate")
    assert verify_delegation(make_delegation(root, delegate), root.public_key) is True


def test_wrong_authority_key_fails():
    root = generate_signer("root")
    attacker = generate_signer("attacker")
    delegate = generate_signer("delegate")
    assert verify_delegation(make_delegation(root, delegate), attacker.public_key) is False


def test_delegate_key_tampering_fails():
    root = generate_signer("root")
    delegate = generate_signer("delegate")
    d = make_delegation(root, delegate)
    forged = SignedDelegation(d.event_id, d.authority_id, d.delegate_id, b"attacker-key", d.signature, d.previous_hash)
    assert verify_delegation(forged, root.public_key) is False


def test_previous_hash_tampering_fails():
    root = generate_signer("root")
    delegate = generate_signer("delegate")
    d = make_delegation(root, delegate)
    forged = SignedDelegation(d.event_id, d.authority_id, d.delegate_id, d.delegate_public_key, d.signature, "f" * 64)
    assert verify_delegation(forged, root.public_key) is False
