"""Root-of-trust rules for PKL key lifecycle events.

The initial authority must be configured out-of-band. Subsequent authority
changes are represented as signed, auditable delegation events.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Authority:
    authority_id: str
    public_key: bytes


@dataclass(frozen=True)
class Delegation:
    authority_id: str
    delegate_id: str
    delegate_public_key: bytes
    event_id: str


class RootOfTrust:
    def __init__(self, root: Authority) -> None:
        self.root = root
        self.delegations: dict[str, Delegation] = {}

    def add_delegation(self, delegation: Delegation, *, authorized_by: str) -> None:
        if authorized_by != self.root.authority_id and authorized_by not in self.delegations:
            raise ValueError("Unauthorized authority")
        if delegation.delegate_id in self.delegations:
            raise ValueError("Delegate already exists")
        self.delegations[delegation.delegate_id] = delegation

    def is_authorized(self, authority_id: str) -> bool:
        return authority_id == self.root.authority_id or authority_id in self.delegations
