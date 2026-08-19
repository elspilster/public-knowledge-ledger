"""Auditable contributor key lifecycle rules."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class KeyRecord:
    contributor_id: str
    key_id: str
    public_key: bytes
    valid_from_event: str
    revoked_at_event: str | None = None
    replaced_by: str | None = None


class KeyRegistry:
    def __init__(self) -> None:
        self._keys: dict[str, KeyRecord] = {}

    def register(self, record: KeyRecord) -> None:
        if record.key_id in self._keys:
            raise ValueError(f"Key already registered: {record.key_id}")
        active = [r for r in self._keys.values() if r.contributor_id == record.contributor_id and r.revoked_at_event is None]
        if active:
            raise ValueError(f"Contributor already has an active key: {record.contributor_id}")
        self._keys[record.key_id] = record

    def revoke(self, key_id: str, revoked_at_event: str, replaced_by: str | None = None) -> KeyRecord:
        record = self._keys[key_id]
        if record.revoked_at_event is not None:
            raise ValueError(f"Key already revoked: {key_id}")
        updated = KeyRecord(record.contributor_id, record.key_id, record.public_key, record.valid_from_event, revoked_at_event, replaced_by)
        self._keys[key_id] = updated
        return updated

    def get(self, key_id: str) -> KeyRecord:
        return self._keys[key_id]

    def is_valid_at(self, key_id: str, event_position: int, positions: dict[str, int]) -> bool:
        record = self._keys[key_id]
        start = positions[record.valid_from_event]
        if event_position < start:
            return False
        if record.revoked_at_event is None:
            return True
        return event_position < positions[record.revoked_at_event]

    def public_keys(self) -> dict[str, bytes]:
        return {key_id: record.public_key for key_id, record in self._keys.items()}
