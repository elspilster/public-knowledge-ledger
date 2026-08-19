"""Auditable 4-of-N root council decisions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from .models import new_id, utc_now
from .quorum import QuorumPolicy, Seat

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
        self.membership_history: list[tuple[str, tuple[Seat, ...]]] = [("initial", policy.seats)]

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

    def update_membership(self, seats: list[Seat], *, reason: str) -> None:
        if not reason.strip():
            raise ValueError("Membership change reason is required")
        next_policy = QuorumPolicy(seats, self.policy.threshold, self.policy.min_categories)
        if set(next_policy.seats) == set(self.policy.seats):
            raise ValueError("Membership is unchanged")
        self.policy = next_policy
        self.membership_history.append((reason, next_policy.seats))

    def history(self, target_id: str | None = None) -> list[CouncilDecision]:
        if target_id is None:
            return list(self.decisions)
        return [d for d in self.decisions if d.target_id == target_id]

    def latest(self, target_id: str) -> CouncilDecision | None:
        matches = self.history(target_id)
        return matches[-1] if matches else None

    def membership_history_records(self) -> list[dict[str, object]]:
        return [{"reason": reason, "seats": [seat.__dict__ for seat in seats]} for reason, seats in self.membership_history]
