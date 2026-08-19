"""Authentication primitives for PKL audit events.

Uses Ed25519 signatures when the optional cryptography dependency is present.
Signatures authenticate an event's canonical contents; they do not establish
that the event's claim is true.
"""

from __future__ import annotations

from dataclasses import dataclass

from .audit import _canonical_event_data

try:
    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
except ImportError:  # pragma: no cover
    InvalidSignature = ValueError  # type: ignore[assignment,misc]
    Ed25519PrivateKey = None  # type: ignore[assignment,misc]
    Ed25519PublicKey = None  # type: ignore[assignment,misc]


@dataclass(frozen=True)
class Signer:
    key_id: str
    private_key: bytes
    public_key: bytes


def generate_signer(key_id: str) -> Signer:
    if Ed25519PrivateKey is None:
        raise RuntimeError("cryptography is required for signed events")
    private = Ed25519PrivateKey.generate()
    return Signer(
        key_id=key_id,
        private_key=private.private_bytes_raw(),
        public_key=private.public_key().public_bytes_raw(),
    )


def sign_event(signer: Signer, event_id: str, event_type: str, object_id: str, timestamp: str, payload: dict, previous_hash: str) -> str:
    if Ed25519PrivateKey is None:
        raise RuntimeError("cryptography is required for signed events")
    private = Ed25519PrivateKey.from_private_bytes(signer.private_key)
    data = _canonical_event_data(event_id, event_type, object_id, timestamp, payload, previous_hash)
    return private.sign(data).hex()


def verify_event_signature(public_key: bytes, signature: str, event_id: str, event_type: str, object_id: str, timestamp: str, payload: dict, previous_hash: str) -> bool:
    if Ed25519PublicKey is None:
        raise RuntimeError("cryptography is required for signed events")
    try:
        public = Ed25519PublicKey.from_public_bytes(public_key)
        data = _canonical_event_data(event_id, event_type, object_id, timestamp, payload, previous_hash)
        public.verify(bytes.fromhex(signature), data)
        return True
    except (ValueError, TypeError, InvalidSignature):
        return False
