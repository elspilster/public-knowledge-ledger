import pytest

from pkl.auth import generate_signer
from pkl.key_registry import KeyRecord, KeyRegistry


def test_key_valid_before_revocation_and_invalid_after():
    signer = generate_signer("human-1")
    registry = KeyRegistry()
    registry.register(KeyRecord("human-1", signer.key_id, signer.public_key, "EVT-1"))
    registry.revoke(signer.key_id, "EVT-4")
    positions = {"EVT-1": 1, "EVT-2": 2, "EVT-4": 4, "EVT-5": 5}

    assert registry.is_valid_at(signer.key_id, 2, positions) is True
    assert registry.is_valid_at(signer.key_id, 4, positions) is False
    assert registry.is_valid_at(signer.key_id, 5, positions) is False


def test_old_signature_can_remain_valid_after_key_rotation():
    old = generate_signer("human-1")
    new = generate_signer("human-1")
    registry = KeyRegistry()
    registry.register(KeyRecord("human-1", old.key_id, old.public_key, "EVT-1"))
    registry.revoke(old.key_id, "EVT-4", replaced_by=new.key_id)
    registry.register(KeyRecord("human-1", new.key_id, new.public_key, "EVT-5"))
    positions = {"EVT-1": 1, "EVT-4": 4, "EVT-5": 5, "EVT-6": 6}

    assert registry.is_valid_at(old.key_id, 3, positions) is True
    assert registry.is_valid_at(old.key_id, 5, positions) is False
    assert registry.is_valid_at(new.key_id, 5, positions) is True


def test_duplicate_key_registration_is_rejected():
    signer = generate_signer("human-1")
    registry = KeyRegistry()
    record = KeyRecord("human-1", signer.key_id, signer.public_key, "EVT-1")
    registry.register(record)
    with pytest.raises(ValueError, match="Key id cannot be reused"):
        registry.register(record)


def test_second_active_key_for_same_contributor_is_rejected():
    first = generate_signer("human-1")
    second = generate_signer("human-1")
    registry = KeyRegistry()
    registry.register(KeyRecord("human-1", first.key_id, first.public_key, "EVT-1"))
    with pytest.raises(ValueError, match="active key"):
        registry.register(KeyRecord("human-1", second.key_id, second.public_key, "EVT-2"))


def test_double_revocation_is_rejected():
    signer = generate_signer("human-1")
    registry = KeyRegistry()
    registry.register(KeyRecord("human-1", signer.key_id, signer.public_key, "EVT-1"))
    registry.revoke(signer.key_id, "EVT-4")
    with pytest.raises(ValueError, match="already revoked"):
        registry.revoke(signer.key_id, "EVT-5")
