"""PKL root council quorum policy."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Seat:
    seat_id: str
    category: str


class QuorumPolicy:
    def __init__(self, seats: list[Seat], threshold: int = 4, min_categories: int = 3) -> None:
        self.seats = tuple(seats)
        self.threshold = threshold
        self.min_categories = min_categories

    def valid(self, signers: set[str]) -> bool:
        if len(signers) < self.threshold:
            return False
        known = {s.seat_id: s for s in self.seats}
        selected = [known[sid] for sid in signers if sid in known]
        if len(selected) != len(signers):
            return False
        return len({s.category for s in selected}) >= self.min_categories

    def capture_possible(self, compromised: set[str]) -> bool:
        return self.valid(compromised)
