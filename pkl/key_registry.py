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
        if not record.contributor_id or not record.key_id or not record.public_key or not record.valid_from_event:
            raise ValueError("Key record fields are required")
        versions = self._keys.get(record.key_id, [])
        if any(r.revoked_at_event is None for r in versions):
            raise ValueError(f"Key already registered: {record.key_id}")
        if versions:
            raise ValueError(f"Key id cannot be reused: {record.key_id}")
        active_contributor = [
            r for records in self._keys.values() for r in records
            if r.contributor_id == record.contributor_id and r.revoked_at_event is None
        ]
        if active_contributor:
            raise ValueError(f"Contributor already has an active key: {record.contributor_id}")
        self._keys.setdefault(record.key_id, []).append(record)

    def revoke(self, key_id: str, revoked_at_event: str, replaced_by: str | None = None) -> KeyRecord:
        if not revoked_at_event:
            raise ValueError("revoked_at_event is required")
        versions = self._keys[key_id]
        record = next((r for r in reversed(versions) if r.revoked_at_event is None), None)
        if record is None:
            raise ValueError(f"Key already revoked: {key_id}")
        if record.valid_from_event == revoked_at_event:
            raise ValueError("Key cannot be revoked at its activation event")
        if replaced_by == key_id:
            raise ValueError("Key cannot replace itself")
        updated = KeyRecord(record.contributor_id, record.key_id, record.public_key, record.valid_from_event, revoked_at_event, replaced_by)
        versions[versions.index(record)] = updated
        return updated

    def get(self, key_id: str) -> KeyRecord:
        versions = self._keys[key_id]
        return next((r for r in reversed(versions) if r.revoked_at_event is None), versions[-1])

    def is_valid_at(self, key_id: str, event_position: int, positions: dict[str, int]) -> bool:
        versions = self._keys.get(key_id)
        if not versions:
            return False
        for record in versions:
            start = positions.get(record.valid_from_event)
            if start is None:
                continue
            end = positions.get(record.revoked_at_event) if record.revoked_at_event is not None else None
            if record.revoked_at_event is not None and end is None:
                continue
            if start <= event_position and (end is None or event_position < end):
                return True
        return False

    def verify(self, positions: dict[str, int]) -> bool:
        """Validate lifecycle ordering and replacement links without mutating state."""
        active_by_contributor: dict[str, str] = {}
        for key_id, versions in self._keys.items():
            if not versions or any(record.key_id != key_id for record in versions):
                return False
            for index, record in enumerate(versions):
                start = positions.get(record.valid_from_event)
                if start is None:
                    return False
                if record.revoked_at_event is None:
                    previous = active_by_contributor.get(record.contributor_id)
                    if previous is not None and previous != key_id:
                        return False
                    active_by_contributor[record.contributor_id] = key_id
                    continue
                end = positions.get(record.revoked_at_event)
                if end is None or end <= start:
                    return False
                if record.replaced_by is not None:
                    replacement = self._keys.get(record.replaced_by)
                    if not replacement:
                        return False
                    replacement_record = replacement[0]
                    replacement_start = positions.get(replacement_record.valid_from_event)
                    if replacement_start is None or replacement_start <= end:
                        return False
                if index + 1 < len(versions):
                    return False
        return True

    def public_keys(self) -> dict[str, bytes]:
        return {key_id: self.get(key_id).public_key for key_id in self._keys}
