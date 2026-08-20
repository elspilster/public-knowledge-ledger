"""Root-of-trust rules for PKL key lifecycle events.

The initial authority is configured out-of-band. Every later delegation must
be cryptographically signed by an authority already in the trust chain.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

from .delegation import SignedDelegation, verify_delegation


_HASH_RE = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True)
class Authority:
    authority_id: str
    public_key: bytes


class RootOfTrust:
    def __init__(self, root: Authority) -> None:
        if not root.authority_id or not root.public_key:
            raise ValueError("Root authority must have an authority_id and public_key")
        self.root = root
        self.delegations: dict[str, SignedDelegation] = {}
        self._event_ids: set[str] = set()

    def authority(self, authority_id: str) -> Authority | None:
        if authority_id == self.root.authority_id:
            return self.root
        delegation = self.delegations.get(authority_id)
        if delegation is None:
            return None
        return Authority(delegation.delegate_id, delegation.delegate_public_key)

    @staticmethod
    def _valid_key_id(authority_id: str, public_key: bytes) -> bool:
        """Ensure a generated key id is cryptographically bound to its public key."""
        if ":" not in authority_id:
            return False
        _, fingerprint = authority_id.rsplit(":", 1)
        return bool(fingerprint) and hashlib.sha256(public_key).hexdigest().startswith(fingerprint)

    def add_delegation(self, delegation: SignedDelegation) -> None:
        if not delegation.event_id:
            raise ValueError("event_id is required")
        if delegation.event_id in self._event_ids:
            raise ValueError("event_id has already been used")
        if not delegation.authority_id or not delegation.delegate_id:
            raise ValueError("authority_id and delegate_id are required")
        if delegation.authority_id == delegation.delegate_id:
            raise ValueError("Self-delegation is not allowed")
        if delegation.delegate_id in self.delegations or delegation.delegate_id == self.root.authority_id:
            raise ValueError("Delegate already exists")
        if not delegation.delegate_public_key:
            raise ValueError("delegate_public_key is required")
        if not _HASH_RE.fullmatch(delegation.previous_hash):
            raise ValueError("Invalid previous_hash")
        if not self._valid_key_id(delegation.delegate_id, delegation.delegate_public_key):
            raise ValueError("Delegate key identity does not match public key")

        issuer = self.authority(delegation.authority_id)
        if issuer is None:
            raise ValueError("Unauthorized authority")

        if not verify_delegation(delegation, issuer.public_key):
            raise ValueError("Invalid delegation signature")

        self.delegations[delegation.delegate_id] = delegation
        self._event_ids.add(delegation.event_id)

    def is_authorized(self, authority_id: str) -> bool:
        return self.authority(authority_id) is not None

    def verify(self) -> bool:
        """Validate all stored delegations without mutating the trust state."""
        seen_events: set[str] = set()
        for delegation in self.delegations.values():
            if delegation.event_id in seen_events:
                return False
            seen_events.add(delegation.event_id)
            if not _HASH_RE.fullmatch(delegation.previous_hash):
                return False
            if not self._valid_key_id(delegation.delegate_id, delegation.delegate_public_key):
                return False
            issuer = self.authority(delegation.authority_id)
            if issuer is None or not verify_delegation(delegation, issuer.public_key):
                return False
        return seen_events == self._event_ids
