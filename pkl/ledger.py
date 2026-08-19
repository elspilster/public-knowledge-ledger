"""Minimal in-memory ledger engine for PKL v0.1.

Every state-changing operation is mirrored into a tamper-evident audit chain.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .audit import AuditChain
from .models import Assessment, Challenge, Claim, Evidence, new_id, utc_now


@dataclass
class LedgerEvent:
    id: str
    event_type: str
    object_id: str
    timestamp: str
    payload: dict[str, Any]


@dataclass
class Ledger:
    claims: dict[str, Claim] = field(default_factory=dict)
    evidence: dict[str, Evidence] = field(default_factory=dict)
    challenges: dict[str, Challenge] = field(default_factory=dict)
    events: list[LedgerEvent] = field(default_factory=list)
    audit: AuditChain = field(default_factory=AuditChain)

    def _record(self, event_type: str, object_id: str, payload: dict[str, Any]) -> None:
        event = LedgerEvent(
            id=new_id("EVT"),
            event_type=event_type,
            object_id=object_id,
            timestamp=utc_now(),
            payload=payload,
        )
        self.events.append(event)
        self.audit.append(event.id, event.event_type, event.object_id, event.timestamp, event.payload)

    def create_claim(self, text: str, contributor_id: str | None = None) -> Claim:
        claim = Claim(id=new_id("PKL"), text=text, contributor_id=contributor_id)
        self.claims[claim.id] = claim
        self._record("claim.created", claim.id, {"text": text})
        return claim

    def add_evidence(self, claim_id: str, title: str, description: str, *, source: str | None = None, contributor_id: str | None = None, supports_claim: bool | None = None) -> Evidence:
        if claim_id not in self.claims:
            raise KeyError(f"Unknown claim: {claim_id}")
        evidence = Evidence(id=new_id("EVD"), claim_id=claim_id, title=title, description=description, source=source, contributor_id=contributor_id, supports_claim=supports_claim)
        self.evidence[evidence.id] = evidence
        self.claims[claim_id].evidence_ids.append(evidence.id)
        self._record("evidence.added", evidence.id, {"claim_id": claim_id})
        return evidence

    def challenge_claim(self, claim_id: str, description: str, *, challenger_id: str | None = None, counter_evidence_ids: list[str] | None = None) -> Challenge:
        if claim_id not in self.claims:
            raise KeyError(f"Unknown claim: {claim_id}")
        counter_evidence_ids = counter_evidence_ids or []
        unknown = [eid for eid in counter_evidence_ids if eid not in self.evidence]
        if unknown:
            raise KeyError(f"Unknown evidence: {unknown}")
        challenge = Challenge(id=new_id("CHL"), target_id=claim_id, description=description, challenger_id=challenger_id, counter_evidence_ids=counter_evidence_ids)
        self.challenges[challenge.id] = challenge
        self.claims[claim_id].challenge_ids.append(challenge.id)
        self._record("challenge.created", challenge.id, {"claim_id": claim_id})
        return challenge

    def assess_claim(self, claim_id: str, status: str, *, evidence_level: str = "E0", summary: str = "") -> Claim:
        if claim_id not in self.claims:
            raise KeyError(f"Unknown claim: {claim_id}")
        if status not in {"proposed", "supported", "disputed", "uncertain", "superseded", "rejected"}:
            raise ValueError(f"Invalid claim status: {status}")
        if evidence_level not in {f"E{i}" for i in range(6)}:
            raise ValueError(f"Invalid evidence level: {evidence_level}")
        claim = self.claims[claim_id]
        claim.status = status  # type: ignore[assignment]
        claim.assessment = Assessment(status=status, evidence_level=evidence_level, summary=summary)  # type: ignore[arg-type]
        self._record("claim.assessed", claim_id, {"status": status, "evidence_level": evidence_level, "summary": summary})
        return claim

    def get_claim(self, claim_id: str) -> Claim:
        return self.claims[claim_id]

    def history(self, object_id: str | None = None) -> list[LedgerEvent]:
        if object_id is None:
            return list(self.events)
        return [event for event in self.events if event.object_id == object_id]

    def verify_history(self) -> bool:
        """Verify the cryptographic audit chain for all ledger events."""
        return self.audit.verify()
