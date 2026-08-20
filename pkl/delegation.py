"""Signed authority delegation primitives for PKL."""

from __future__ import annotations

from dataclasses import dataclass

from .auth import verify_event_signature
from .audit import _canonical_event_data


@dataclass(frozen=True)
class SignedDelegation:
    event_id: str
    authority_id: str
    delegate_id: str
    delegate_public_key: bytes
    signature: str
    previous_hash: str


def delegation_bytes(d: SignedDelegation) -> bytes:
    return _canonical_event_data(
        d.event_id,
        "authority.delegated",
        d.delegate_id,
        d.event_id,
        {"authority_id": d.authority_id, "delegate_id": d.delegate_id, "delegate_public_key": d.delegate_public_key.hex()},
        d.previous_hash,
        d.authority_id,
    )


def verify_delegation(d: SignedDelegation, authority_public_key: bytes) -> bool:
    return verify_event_signature(
        authority_public_key,
        d.signature,
        d.event_id,
        "authority.delegated",
        d.delegate_id,
        d.event_id,
        {"authority_id": d.authority_id, "delegate_id": d.delegate_id, "delegate_public_key": d.delegate_public_key.hex()},
        d.previous_hash,
        d.authority_id,
    )
