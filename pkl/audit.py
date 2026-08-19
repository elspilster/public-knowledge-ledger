"""Tamper-evident event chain for PKL history.

This provides integrity evidence, not cryptographic proof of truth. The chain
makes unauthorised alteration of an existing event detectable when the chain
is verified.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from typing import Any


@dataclass(frozen=True)
class AuditEvent:
    event_id: str
    event_type: str
    object_id: str
    timestamp: str
    payload: dict[str, Any]
    previous_hash: str
    event_hash: str


def _canonical_event_data(event_id: str, event_type: str, object_id: str, timestamp: str, payload: dict[str, Any], previous_hash: str) -> bytes:
    data = {
        "event_id": event_id,
        "event_type": event_type,
        "object_id": object_id,
        "timestamp": timestamp,
        "payload": payload,
        "previous_hash": previous_hash,
    }
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def calculate_hash(event_id: str, event_type: str, object_id: str, timestamp: str, payload: dict[str, Any], previous_hash: str) -> str:
    return hashlib.sha256(
        _canonical_event_data(event_id, event_type, object_id, timestamp, payload, previous_hash)
    ).hexdigest()


class AuditChain:
    """Append-only-in-memory event chain with verification."""

    def __init__(self) -> None:
        self.events: list[AuditEvent] = []

    def append(self, event_id: str, event_type: str, object_id: str, timestamp: str, payload: dict[str, Any]) -> AuditEvent:
        previous_hash = self.events[-1].event_hash if self.events else "0" * 64
        event_hash = calculate_hash(event_id, event_type, object_id, timestamp, payload, previous_hash)
        event = AuditEvent(event_id, event_type, object_id, timestamp, payload, previous_hash, event_hash)
        self.events.append(event)
        return event

    def verify(self) -> bool:
        previous_hash = "0" * 64
        for event in self.events:
            expected = calculate_hash(
                event.event_id,
                event.event_type,
                event.object_id,
                event.timestamp,
                event.payload,
                previous_hash,
            )
            if event.previous_hash != previous_hash or event.event_hash != expected:
                return False
            previous_hash = event.event_hash
        return True

    def snapshot(self) -> list[dict[str, Any]]:
        return [asdict(event) for event in self.events]
