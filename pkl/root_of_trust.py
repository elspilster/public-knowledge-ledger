"""Root-of-trust rules for PKL key lifecycle events.

The initial authority is configured out-of-band. Every later delegation must
be cryptographically signed by an authority already in the trust chain.
"""

from __future__ import annotations

from dataclasses import dataclass

from .delegation import SignedDelegation, verify_delegation


@dataclass(frozen=True)
class Authority:
    authority_id: str
    public_key: bytes


class RootOfTrust:
    def __init__(self, root: Authority) -> None:
        self.root = root
        self.delegations: dict[str, SignedDelegation] = {}

    def authority(self, authority_id: str) -> Authority | None:
        if authority_id == self.root.authority_id:
            return self.root
        delegation = self.delegations.get(authority_id)
        if delegation is None:
            return None
        return Authority(delegation.delegate_id, delegation.delegate_public_key)

    def add_delegation(self, delegation: SignedDelegation) -> None:
        if delegation.delegate_id in self.delegations:
            raise ValueError("Delegate already exists")

        issuer = self.authority(delegation.authority_id)
        if issuer is None:
            raise ValueError("Unauthorized authority")

        if not verify_delegation(delegation, issuer.public_key):
            raise ValueError("Invalid delegation signature")

        if delegation.authority_id == delegation.delegate_id:
            raise ValueError("Self-delegation is not allowed")

        self.delegations[delegation.delegate_id] = delegation

    def is_authorized(self, authority_id: str) -> bool:
        return self.authority(authority_id) is not None
