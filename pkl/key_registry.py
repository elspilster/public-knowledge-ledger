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
        self._keys: dict[str, list[KeyRecord]] = {}

    def register(self, record: KeyRecord) -> None:
        versions = self._keys.get(record.key_id, [])
        if any(r.revoked_at_event is None for r in versions):
            raise ValueError(f"Key already registered: {record.key_id}")
        active_contributor = [
            r for records in self._keys.values() for r in records
            if r.contributor_id == record.contributor_id and r.revoked_at_event is None
        ]
        if active_contributor:
            raise ValueError(f"Contributor already has an active key: {record.contributor_id}")
        self._keys.setdefault(record.key_id, []).append(record)

    def revoke(self, key_id: str, revoked_at_event: str, replaced_by: str | None = None) -> KeyRecord:
        versions = self._keys[key_id]
        record = next((r for r in reversed(versions) if r.revoked_at_event is None), None)
        if record is None:
            raise ValueError(f"Key already revoked: {key_id}")
        updated = KeyRecord(record.contributor_id, record.key_id, record.public_key, record.valid_from_event, revoked_at_event, replaced_by)
        versions[versions.index(record)] = updated
        return updated

    def get(self, key_id: str) -> KeyRecord:
        versions = self._keys[key_id]
        return next((r for r in reversed(versions) if r.revoked_at_event is None), versions[-1])

    def is_valid_at(self, key_id: str, event_position: int, positions: dict[str, int]) -> bool:
        versions = self._keys[key_id]
        for record in versions:
            start = positions[record.valid_from_event]
            end = positions[record.revoked_at_event] if record.revoked_at_event is not None else None
            if start <= event_position and (end is None or event_position < end):
                return True
        return False

    def public_keys(self) -> dict[str, bytes]:
        return {key_id: self.get(key_id).public_key for key_id in self._keys}
