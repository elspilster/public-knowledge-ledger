import pytest

from pkl.auth import generate_signer
from pkl.root_of_trust import Authority, Delegation, RootOfTrust


def test_root_authority_is_authorized():
    root = generate_signer("root")
    trust = RootOfTrust(Authority("root", root.public_key))
    assert trust.is_authorized("root") is True


def test_unknown_authority_cannot_delegate():
    root = generate_signer("root")
    trust = RootOfTrust(Authority("root", root.public_key))
    with pytest.raises(ValueError, match="Unauthorized"):
        trust.add_delegation(Delegation("attacker", "delegate", b"bad", "EVT-1"), authorized_by="attacker")


def test_root_can_delegate():
    root = generate_signer("root")
    delegate = generate_signer("delegate")
    trust = RootOfTrust(Authority("root", root.public_key))
    trust.add_delegation(Delegation("root", "delegate", delegate.public_key, "EVT-1"), authorized_by="root")
    assert trust.is_authorized("delegate") is True


def test_duplicate_delegate_is_rejected():
    root = generate_signer("root")
    delegate = generate_signer("delegate")
    trust = RootOfTrust(Authority("root", root.public_key))
    d = Delegation("root", "delegate", delegate.public_key, "EVT-1")
    trust.add_delegation(d, authorized_by="root")
    with pytest.raises(ValueError, match="already exists"):
        trust.add_delegation(d, authorized_by="root")


def test_fake_root_id_does_not_create_authority_without_matching_configured_root():
    real_root = generate_signer("real-root")
    attacker = generate_signer("root")
    trust = RootOfTrust(Authority("real-root", real_root.public_key))
    with pytest.raises(ValueError, match="Unauthorized"):
        trust.add_delegation(Delegation("root", "delegate", attacker.public_key, "EVT-1"), authorized_by="root")
