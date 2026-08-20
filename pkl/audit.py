"""Tamper-evident and optionally authenticated PKL history."""

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
    signer_key_id: str | None = None
    signature: str | None = None


def _canonical_event_data(
    event_id: str,
    event_type: str,
    object_id: str,
    timestamp: str,
    payload: dict[str, Any],
    previous_hash: str,
    signer_key_id: str | None = None,
) -> bytes:
    data = {
        "event_id": event_id,
        "event_type": event_type,
        "object_id": object_id,
        "timestamp": timestamp,
        "payload": payload,
        "previous_hash": previous_hash,
        "signer_key_id": signer_key_id,
    }
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def calculate_hash(
    event_id: str,
    event_type: str,
    object_id: str,
    timestamp: str,
    payload: dict[str, Any],
    previous_hash: str,
    signer_key_id: str | None = None,
) -> str:
    return hashlib.sha256(
        _canonical_event_data(event_id, event_type, object_id, timestamp, payload, previous_hash, signer_key_id)
    ).hexdigest()


class AuditChain:
    def __init__(self) -> None:
        self.events: list[AuditEvent] = []

    def append(
        self,
        event_id: str,
        event_type: str,
        object_id: str,
        timestamp: str,
        payload: dict[str, Any],
        *,
        signer_key_id: str | None = None,
        signature: str | None = None,
    ) -> AuditEvent:
        previous_hash = self.events[-1].event_hash if self.events else "0" * 64
        event_hash = calculate_hash(
            event_id,
            event_type,
            object_id,
            timestamp,
            payload,
            previous_hash,
            signer_key_id,
        )
        event = AuditEvent(event_id, event_type, object_id, timestamp, payload, previous_hash, event_hash, signer_key_id, signature)
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
                event.signer_key_id,
            )
            if event.previous_hash != previous_hash or event.event_hash != expected:
                return False
            previous_hash = event.event_hash
        return True

    def verify_signatures(self, public_keys: dict[str, bytes], *, require_signatures: bool = False) -> bool:
        """Verify event signatures; strict mode rejects unsigned or partially signed events."""
        from .auth import verify_event_signature

        for event in self.events:
            if event.signature is None or event.signer_key_id is None:
                if require_signatures:
                    return False
                continue
            public_key = public_keys.get(event.signer_key_id)
            if public_key is None or not verify_event_signature(
                public_key,
                event.signature,
                event.event_id,
                event.event_type,
                event.object_id,
                event.timestamp,
                event.payload,
                event.previous_hash,
                event.signer_key_id,
            ):
                return False
        return True

    def snapshot(self) -> list[dict[str, Any]]:
        return [asdict(event) for event in self.events]
