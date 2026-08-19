"""Auditable 4-of-N root council decisions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from .models import new_id, utc_now
from .quorum import QuorumPolicy


DecisionStatus = Literal["accepted", "rejected"]


@dataclass(frozen=True)
class CouncilDecision:
    id: str
    target_id: str
    decision: DecisionStatus
    signers: frozenset[str]
    rationale: str
    created_at: str = field(default_factory=utc_now)


class RootCouncil:
    def __init__(self, policy: QuorumPolicy) -> None:
        self.policy = policy
        self.decisions: list[CouncilDecision] = []

    def decide(self, target_id: str, decision: DecisionStatus, signers: set[str], rationale: str) -> CouncilDecision:
        if not target_id:
            raise ValueError("target_id is required")
        if decision not in {"accepted", "rejected"}:
            raise ValueError("Invalid council decision")
        if not rationale.strip():
            raise ValueError("Council rationale is required")
        if not self.policy.valid(signers):
            raise ValueError("Quorum not satisfied")
        record = CouncilDecision(new_id("DEC"), target_id, decision, frozenset(signers), rationale)
        self.decisions.append(record)
        return record

    def history(self, target_id: str | None = None) -> list[CouncilDecision]:
        if target_id is None:
            return list(self.decisions)
        return [d for d in self.decisions if d.target_id == target_id]

    def latest(self, target_id: str) -> CouncilDecision | None:
        matches = self.history(target_id)
        return matches[-1] if matches else None
