import pytest

from pkl.auth import generate_signer, sign_event
from pkl.delegation import SignedDelegation
from pkl.root_of_trust import Authority, RootOfTrust


def delegation(authority, delegate, *, event_id="EVT-1", previous_hash="0" * 64, delegate_id=None):
    delegate_id = delegate_id or delegate.key_id
    payload = {"authority_id": authority.key_id, "delegate_id": delegate_id, "delegate_public_key": delegate.public_key.hex()}
    signature = sign_event(authority, event_id, "authority.delegated", delegate_id, event_id, payload, previous_hash)
    return SignedDelegation(event_id, authority.key_id, delegate_id, delegate.public_key, signature, previous_hash)


def test_duplicate_event_id_replay_is_rejected():
    root = generate_signer("root")
    first = generate_signer("delegate-1")
    second = generate_signer("delegate-2")
    trust = RootOfTrust(Authority(root.key_id, root.public_key))
    trust.add_delegation(delegation(root, first))
    with pytest.raises(ValueError, match="event_id"):
        trust.add_delegation(delegation(root, second))


def test_delegate_cannot_replace_existing_authority_key():
    root = generate_signer("root")
    delegate = generate_signer("delegate")
    replacement = generate_signer("replacement")
    trust = RootOfTrust(Authority(root.key_id, root.public_key))
    trust.add_delegation(delegation(root, delegate))
    forged = delegation(root, replacement, delegate_id=delegate.key_id)
    with pytest.raises(ValueError, match="already exists"):
        trust.add_delegation(forged)


def test_delegation_with_invalid_previous_hash_is_rejected():
    root = generate_signer("root")
    delegate = generate_signer("delegate")
    trust = RootOfTrust(Authority(root.key_id, root.public_key))
    forged = delegation(root, delegate, previous_hash="not-a-valid-hash")
    with pytest.raises(ValueError, match="previous_hash"):
        trust.add_delegation(forged)


def test_delegation_event_id_must_not_be_reused():
    root = generate_signer("root")
    delegate = generate_signer("delegate")
    trust = RootOfTrust(Authority(root.key_id, root.public_key))
    trust.add_delegation(delegation(root, delegate))
    another = generate_signer("another")
    with pytest.raises(ValueError, match="event_id"):
        trust.add_delegation(delegation(root, another))


def test_root_key_cannot_be_delegated_as_a_different_authority():
    root = generate_signer("root")
    attacker = generate_signer("attacker")
    trust = RootOfTrust(Authority(root.key_id, root.public_key))
    forged = delegation(root, attacker, delegate_id=root.key_id)
    with pytest.raises(ValueError, match="already exists"):
        trust.add_delegation(forged)
