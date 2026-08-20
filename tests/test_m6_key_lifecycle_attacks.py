import pytest

from pkl.auth import generate_signer
from pkl.key_registry import KeyRecord, KeyRegistry


def test_revoked_key_id_cannot_be_reused():
    signer = generate_signer("human-1")
    registry = KeyRegistry()
    registry.register(KeyRecord("human-1", signer.key_id, signer.public_key, "EVT-1"))
    registry.revoke(signer.key_id, "EVT-4")
    with pytest.raises(ValueError, match="cannot be reused"):
        registry.register(KeyRecord("human-1", signer.key_id, signer.public_key, "EVT-5"))


def test_revoke_cannot_happen_at_activation_event():
    signer = generate_signer("human-1")
    registry = KeyRegistry()
    registry.register(KeyRecord("human-1", signer.key_id, signer.public_key, "EVT-1"))
    with pytest.raises(ValueError, match="activation event"):
        registry.revoke(signer.key_id, "EVT-1")


def test_key_cannot_replace_itself():
    signer = generate_signer("human-1")
    registry = KeyRegistry()
    registry.register(KeyRecord("human-1", signer.key_id, signer.public_key, "EVT-1"))
    with pytest.raises(ValueError, match="replace itself"):
        registry.revoke(signer.key_id, "EVT-4", replaced_by=signer.key_id)


def test_unknown_key_and_unknown_position_are_rejected_without_mutation():
    registry = KeyRegistry()
    assert registry.is_valid_at("missing:key", 2, {}) is False


def test_registry_verify_rejects_missing_replacement():
    old = generate_signer("human-1")
    replacement = generate_signer("human-1")
    registry = KeyRegistry()
    registry.register(KeyRecord("human-1", old.key_id, old.public_key, "EVT-1"))
    registry.revoke(old.key_id, "EVT-4", replaced_by=replacement.key_id)
    positions = {"EVT-1": 1, "EVT-4": 4}
    assert registry.verify(positions) is False


def test_registry_verify_accepts_ordered_rotation():
    old = generate_signer("human-1")
    new = generate_signer("human-1")
    registry = KeyRegistry()
    registry.register(KeyRecord("human-1", old.key_id, old.public_key, "EVT-1"))
    registry.revoke(old.key_id, "EVT-4", replaced_by=new.key_id)
    registry.register(KeyRecord("human-1", new.key_id, new.public_key, "EVT-5"))
    positions = {"EVT-1": 1, "EVT-4": 4, "EVT-5": 5}
    assert registry.verify(positions) is True


def test_registry_verify_rejects_replacement_before_revocation():
    old = generate_signer("human-1")
    new = generate_signer("human-1")
    registry = KeyRegistry()
    registry.register(KeyRecord("human-1", old.key_id, old.public_key, "EVT-1"))
    registry.revoke(old.key_id, "EVT-5", replaced_by=new.key_id)
    registry.register(KeyRecord("human-1", new.key_id, new.public_key, "EVT-3"))
    positions = {"EVT-1": 1, "EVT-3": 3, "EVT-5": 5}
    assert registry.verify(positions) is False
