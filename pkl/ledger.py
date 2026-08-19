"""Minimal in-memory ledger engine for PKL v0.1.

Every state-changing operation is mirrored into a tamper-evident audit chain.
The audit history can also be replayed to verify the current ledger state.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
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
        event = LedgerEvent(id=new_id("EVT"), event_type=event_type, object_id=object_id, timestamp=utc_now(), payload=payload)
        self.events.append(event)
        self.audit.append(event.id, event.event_type, event.object_id, event.timestamp, event.payload)

    def create_claim(self, text: str, contributor_id: str | None = None) -> Claim:
        claim = Claim(id=new_id("PKL"), text=text, contributor_id=contributor_id)
        self.claims[claim.id] = claim
        self._record("claim.created", claim.id, {"text": text, "contributor_id": contributor_id})
        return claim

    def add_evidence(self, claim_id: str, title: str, description: str, *, source: str | None = None, contributor_id: str | None = None, supports_claim: bool | None = None) -> Evidence:
        if claim_id not in self.claims:
            raise KeyError(f"Unknown claim: {claim_id}")
        evidence = Evidence(id=new_id("EVD"), claim_id=claim_id, title=title, description=description, source=source, contributor_id=contributor_id, supports_claim=supports_claim)
        self.evidence[evidence.id] = evidence
        self.claims[claim_id].evidence_ids.append(evidence.id)
        self._record("evidence.added", evidence.id, {"claim_id": claim_id, "title": title, "description": description, "source": source, "contributor_id": contributor_id, "supports_claim": supports_claim})
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
        self._record("challenge.created", challenge.id, {"claim_id": claim_id, "description": description, "challenger_id": challenger_id, "counter_evidence_ids": counter_evidence_ids})
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
        return self.audit.verify()

    def replay_state(self) -> dict[str, dict[str, Any]]:
        """Reconstruct a minimal canonical state from the audit history."""
        claims: dict[str, dict[str, Any]] = {}
        evidence: dict[str, dict[str, Any]] = {}
        challenges: dict[str, dict[str, Any]] = {}
        for event in self.audit.events:
            payload = event.payload
            if event.event_type == "claim.created":
                claims[event.object_id] = {
                    "id": event.object_id,
                    "text": payload["text"],
                    "contributor_id": payload.get("contributor_id"),
                    "status": "proposed",
                }
            elif event.event_type == "evidence.added":
                evidence[event.object_id] = {
                    "id": event.object_id,
                    "claim_id": payload["claim_id"],
                    "title": payload["title"],
                    "description": payload["description"],
                    "source": payload.get("source"),
                    "contributor_id": payload.get("contributor_id"),
                    "supports_claim": payload.get("supports_claim"),
                }
            elif event.event_type == "challenge.created":
                challenges[event.object_id] = {
                    "id": event.object_id,
                    "target_id": payload["claim_id"],
                    "description": payload["description"],
                    "challenger_id": payload.get("challenger_id"),
                    "counter_evidence_ids": payload.get("counter_evidence_ids", []),
                }
            elif event.event_type == "claim.assessed":
                if event.object_id not in claims:
                    raise ValueError(f"Assessment references unknown claim: {event.object_id}")
                claims[event.object_id]["status"] = payload["status"]
                claims[event.object_id]["evidence_level"] = payload["evidence_level"]
                claims[event.object_id]["summary"] = payload["summary"]
            else:
                raise ValueError(f"Unknown audit event type: {event.event_type}")
        return {"claims": claims, "evidence": evidence, "challenges": challenges}

    def current_state(self) -> dict[str, dict[str, Any]]:
        """Return the same canonical subset from the live ledger state."""
        return {
            "claims": {
                key: {
                    "id": claim.id,
                    "text": claim.text,
                    "contributor_id": claim.contributor_id,
                    "status": claim.status,
                    "evidence_level": claim.assessment.evidence_level,
                    "summary": claim.assessment.summary,
                }
                for key, claim in self.claims.items()
            },
            "evidence": {
                key: {
                    "id": item.id,
                    "claim_id": item.claim_id,
                    "title": item.title,
                    "description": item.description,
                    "source": item.source,
                    "contributor_id": item.contributor_id,
                    "supports_claim": item.supports_claim,
                }
                for key, item in self.evidence.items()
            },
            "challenges": {
                key: {
                    "id": item.id,
                    "target_id": item.target_id,
                    "description": item.description,
                    "challenger_id": item.challenger_id,
                    "counter_evidence_ids": item.counter_evidence_ids,
                }
                for key, item in self.challenges.items()
            },
        }

    def verify_state(self) -> bool:
        """Verify both audit integrity and agreement with replayed state."""
        if not self.verify_history():
            return False
        try:
            return self.replay_state() == self.current_state()
        except (KeyError, TypeError, ValueError):
            return False

    def verify(self) -> bool:
        """Full integrity check: history and current state."""
        return self.verify_state()
