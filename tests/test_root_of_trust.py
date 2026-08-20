import pytest

from pkl.auth import generate_signer, sign_event
from pkl.delegation import SignedDelegation
from pkl.root_of_trust import Authority, RootOfTrust


def make_delegation(authority, delegate, event_id="EVT-1", previous_hash="0" * 64):
    payload = {
        "authority_id": authority.key_id,
        "delegate_id": delegate.key_id,
        "delegate_public_key": delegate.public_key.hex(),
    }
    signature = sign_event(authority, event_id, "authority.delegated", delegate.key_id, event_id, payload, previous_hash, signer_key_id=authority.key_id)
    return SignedDelegation(event_id, authority.key_id, delegate.key_id, delegate.public_key, signature, previous_hash)


def test_root_authority_is_authorized():
    root = generate_signer("root")
    trust = RootOfTrust(Authority(root.key_id, root.public_key))
    assert trust.is_authorized(root.key_id) is True


def test_unknown_authority_cannot_delegate():
    root = generate_signer("root")
    attacker = generate_signer("attacker")
    delegate = generate_signer("delegate")
    trust = RootOfTrust(Authority(root.key_id, root.public_key))
    forged = make_delegation(attacker, delegate)
    with pytest.raises(ValueError, match="Unauthorized"):
        trust.add_delegation(forged)


def test_root_can_delegate_with_valid_signature():
    root = generate_signer("root")
    delegate = generate_signer("delegate")
    trust = RootOfTrust(Authority(root.key_id, root.public_key))
    trust.add_delegation(make_delegation(root, delegate))
    assert trust.is_authorized(delegate.key_id) is True


def test_wrong_signature_key_is_rejected():
    root = generate_signer("root")
    attacker = generate_signer("attacker")
    delegate = generate_signer("delegate")
    trust = RootOfTrust(Authority(root.key_id, root.public_key))
    forged = make_delegation(attacker, delegate)
    with pytest.raises(ValueError, match="Invalid delegation signature"):
        trust.add_delegation(SignedDelegation(forged.event_id, root.key_id, forged.delegate_id, forged.delegate_public_key, forged.signature, forged.previous_hash))


def test_tampered_delegate_key_is_rejected():
    root = generate_signer("root")
    delegate = generate_signer("delegate")
    attacker_key = generate_signer("attacker").public_key
    trust = RootOfTrust(Authority(root.key_id, root.public_key))
    forged = make_delegation(root, delegate)
    forged = SignedDelegation(forged.event_id, forged.authority_id, forged.delegate_id, attacker_key, forged.signature, forged.previous_hash)
    with pytest.raises(ValueError, match="Invalid delegation signature"):
        trust.add_delegation(forged)


def test_duplicate_delegate_is_rejected():
    root = generate_signer("root")
    delegate = generate_signer("delegate")
    trust = RootOfTrust(Authority(root.key_id, root.public_key))
    delegation = make_delegation(root, delegate)
    trust.add_delegation(delegation)
    with pytest.raises(ValueError, match="already exists"):
        trust.add_delegation(delegation)


def test_self_delegation_is_rejected():
    root = generate_signer("root")
    trust = RootOfTrust(Authority(root.key_id, root.public_key))
    with pytest.raises(ValueError, match="Self-delegation"):
        trust.add_delegation(make_delegation(root, root))
