"""Minimal in-memory ledger engine for PKL v0.1."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .audit import AuditChain
from .key_registry import KeyRecord, KeyRegistry
from .models import Assessment, AssessmentReview, Challenge, Claim, Evidence, EvidenceProfile, new_id, utc_now
from .provenance import ProvenanceGraph, Relation
from .replay import replay


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
    assessment_reviews: dict[str, AssessmentReview] = field(default_factory=dict)
    provenance: ProvenanceGraph = field(default_factory=ProvenanceGraph)
    events: list[LedgerEvent] = field(default_factory=list)
    audit: AuditChain = field(default_factory=AuditChain)
    keys: KeyRegistry = field(default_factory=KeyRegistry)

    def _record(self, event_type: str, object_id: str, payload: dict[str, Any]) -> None:
        event = LedgerEvent(id=new_id("EVT"), event_type=event_type, object_id=object_id, timestamp=utc_now(), payload=payload)
        self.events.append(event)
        self.audit.append(event.id, event.event_type, event.object_id, event.timestamp, event.payload)

    def register_key(self, contributor_id: str, key_id: str, public_key: bytes) -> KeyRecord:
        if not contributor_id or not key_id or not public_key:
            raise ValueError("contributor_id, key_id and public_key are required")
        event_id = new_id("EVT")
        timestamp = utc_now()
        record = KeyRecord(contributor_id, key_id, public_key, event_id)
        self.keys.register(record)
        payload = {"contributor_id": contributor_id, "key_id": key_id, "public_key": public_key.hex(), "valid_from_event": event_id}
        self.events.append(LedgerEvent(event_id, "key.registered", key_id, timestamp, payload))
        self.audit.append(event_id, "key.registered", key_id, timestamp, payload)
        return record

    def revoke_key(self, key_id: str, replaced_by: str | None = None) -> KeyRecord:
        event_id = new_id("EVT")
        timestamp = utc_now()
        if replaced_by is not None:
            replacement = self.keys.get(replaced_by)
            if replacement.revoked_at_event is not None:
                raise ValueError("Replacement key is revoked")
            if replacement.contributor_id != self.keys.get(key_id).contributor_id:
                raise ValueError("Replacement key belongs to a different contributor")
        updated = self.keys.revoke(key_id, event_id, replaced_by)
        payload = {"contributor_id": updated.contributor_id, "key_id": key_id, "revoked_at_event": event_id, "replaced_by": replaced_by}
        self.events.append(LedgerEvent(event_id, "key.revoked", key_id, timestamp, payload))
        self.audit.append(event_id, "key.revoked", key_id, timestamp, payload)
        return updated

    def _record_claim_event(self, event_type: str, object_id: str, payload: dict[str, Any]) -> None:
        self._record(event_type, object_id, payload)

    def create_claim(self, text: str, contributor_id: str | None = None) -> Claim:
        if not text or not text.strip():
            raise ValueError("Claim text is required")
        claim = Claim(id=new_id("PKL"), text=text, contributor_id=contributor_id)
        self.claims[claim.id] = claim
        self._record_claim_event("claim.created", claim.id, {"text": text, "contributor_id": contributor_id})
        return claim

    def correct_claim(self, claim_id: str, corrected_text: str, *, reason: str, contributor_id: str | None = None) -> Claim:
        if claim_id not in self.claims:
            raise KeyError(f"Unknown claim: {claim_id}")
        if not corrected_text or not corrected_text.strip():
            raise ValueError("Corrected claim text is required")
        if not reason or not reason.strip():
            raise ValueError("Correction reason is required")
        claim = self.claims[claim_id]
        previous_text = claim.text
        claim.text = corrected_text
        self._record("claim.corrected", claim_id, {"previous_text": previous_text, "corrected_text": corrected_text, "reason": reason, "contributor_id": contributor_id})
        return claim

    def add_evidence(self, claim_id: str, title: str, description: str, *, source: str | None = None, contributor_id: str | None = None, supports_claim: bool | None = None, profile: EvidenceProfile | None = None, metadata: dict[str, Any] | None = None) -> Evidence:
        if claim_id not in self.claims:
            raise KeyError(f"Unknown claim: {claim_id}")
        if not title or not description:
            raise ValueError("Evidence title and description are required")
        profile = profile or EvidenceProfile()
        profile.validate()
        evidence = Evidence(id=new_id("EVD"), claim_id=claim_id, title=title, description=description, source=source, contributor_id=contributor_id, supports_claim=supports_claim, profile=profile, metadata=dict(metadata or {}))
        self.evidence[evidence.id] = evidence
        self.claims[claim_id].evidence_ids.append(evidence.id)
        self._record("evidence.added", evidence.id, {"claim_id": claim_id, "title": title, "description": description, "source": source, "contributor_id": contributor_id, "supports_claim": supports_claim, "profile": profile.as_dict(), "metadata": evidence.metadata})
        return evidence

    def update_evidence_profile(self, evidence_id: str, profile: EvidenceProfile) -> Evidence:
        if evidence_id not in self.evidence:
            raise KeyError(f"Unknown evidence: {evidence_id}")
        profile.validate()
        evidence = self.evidence[evidence_id]
        evidence.profile = profile
        self._record("evidence.profile_updated", evidence_id, {"profile": profile.as_dict()})
        return evidence

    def link_evidence(self, source_id: str, target_id: str, relation: Relation, note: str = "") -> None:
        if source_id not in self.evidence or target_id not in self.evidence:
            raise KeyError("Provenance links must reference known evidence")
        edge = self.provenance.add(source_id, target_id, relation, note)
        self._record("evidence.provenance_linked", source_id, {"source_id": edge.source_id, "target_id": edge.target_id, "relation": edge.relation, "note": edge.note})

    def evidence_independence(self, first_id: str, second_id: str) -> str:
        if first_id not in self.evidence or second_id not in self.evidence:
            raise KeyError("Independence checks must reference known evidence")
        return self.provenance.independence_hint(first_id, second_id)

    def challenge_claim(self, claim_id: str, description: str, *, challenger_id: str | None = None, counter_evidence_ids: list[str] | None = None) -> Challenge:
        if claim_id not in self.claims:
            raise KeyError(f"Unknown claim: {claim_id}")
        if not description:
            raise ValueError("Challenge description is required")
        counter_evidence_ids = counter_evidence_ids or []
        unknown = [eid for eid in counter_evidence_ids if eid not in self.evidence]
        if unknown:
            raise KeyError(f"Unknown evidence: {unknown}")
        challenge = Challenge(id=new_id("CHL"), target_id=claim_id, description=description, challenger_id=challenger_id, counter_evidence_ids=counter_evidence_ids)
        self.challenges[challenge.id] = challenge
        self.claims[claim_id].challenge_ids.append(challenge.id)
        self._record("challenge.created", challenge.id, {"claim_id": claim_id, "description": description, "challenger_id": challenger_id, "counter_evidence_ids": counter_evidence_ids})
        return challenge

    def resolve_challenge(self, challenge_id: str, resolution: str, *, resolver_id: str | None = None) -> Challenge:
        if challenge_id not in self.challenges:
            raise KeyError(f"Unknown challenge: {challenge_id}")
        if not resolution or not resolution.strip():
            raise ValueError("Challenge resolution is required")
        challenge = self.challenges[challenge_id]
        if challenge.status != "open":
            raise ValueError("Challenge is already resolved")
        challenge.status = "resolved"
        challenge.resolution = resolution
        self._record("challenge.resolved", challenge_id, {"resolution": resolution, "resolver_id": resolver_id})
        return challenge

    def assess_claim(self, claim_id: str, status: str, *, evidence_level: str = "E0", summary: str = "") -> Claim:
        if claim_id not in self.claims:
            raise KeyError(f"Unknown claim: {claim_id}")
        if status not in {"proposed", "supported", "disputed", "uncertain", "superseded", "rejected"}:
            raise ValueError(f"Invalid claim status: {status}")
        if evidence_level not in {f"E{i}" for i in range(6)}:
            raise ValueError(f"Invalid evidence level: {evidence_level}")
        claim = self.claims[claim_id]
        assessment = Assessment(status=status, evidence_level=evidence_level, summary=summary)
        claim.status = status  # type: ignore[assignment]
        claim.assessment = assessment  # type: ignore[assignment]
        history_item = {"status": status, "evidence_level": evidence_level, "summary": summary, "assessed_at": assessment.assessed_at}
        claim.assessment_history.append(history_item)
        self._record("claim.assessed", claim_id, history_item)
        return claim

    def review_assessment(self, claim_id: str, reviewer_id: str, status: str, *, rationale: str) -> AssessmentReview:
        if claim_id not in self.claims:
            raise KeyError(f"Unknown claim: {claim_id}")
        if not reviewer_id:
            raise ValueError("reviewer_id is required")
        if status not in {"proposed", "supported", "disputed", "uncertain", "superseded", "rejected"}:
            raise ValueError(f"Invalid review status: {status}")
        if not rationale or not rationale.strip():
            raise ValueError("Review rationale is required")
        review = AssessmentReview(new_id("REV"), claim_id, reviewer_id, status, rationale)
        self.assessment_reviews[review.id] = review
        self.claims[claim_id].assessment_review_ids.append(review.id)
        self._record("assessment.reviewed", review.id, {"claim_id": claim_id, "reviewer_id": reviewer_id, "status": status, "rationale": rationale, "created_at": review.created_at})
        return review

    def get_claim(self, claim_id: str) -> Claim:
        return self.claims[claim_id]

    def history(self, object_id: str | None = None) -> list[LedgerEvent]:
        if object_id is None:
            return list(self.events)
        return [event for event in self.events if event.object_id == object_id]

    def verify_history(self) -> bool:
        return self.audit.verify()

    def replay_state(self) -> dict[str, Any]:
        state = replay(self.audit.events)
        return {"claims": state.claims, "evidence": state.evidence, "challenges": state.challenges, "assessment_reviews": state.assessment_reviews, "provenance": state.provenance}

    def current_state(self) -> dict[str, Any]:
        return {
            "claims": {key: {"id": claim.id, "text": claim.text, "contributor_id": claim.contributor_id, "status": claim.status, "evidence_level": claim.assessment.evidence_level, "summary": claim.assessment.summary, "assessment_history": claim.assessment_history, "assessment_review_ids": claim.assessment_review_ids} for key, claim in self.claims.items()},
            "evidence": {key: {"id": item.id, "claim_id": item.claim_id, "title": item.title, "description": item.description, "source": item.source, "contributor_id": item.contributor_id, "supports_claim": item.supports_claim, "profile": item.profile.as_dict(), "metadata": item.metadata} for key, item in self.evidence.items()},
            "challenges": {key: {"id": item.id, "target_id": item.target_id, "description": item.description, "challenger_id": item.challenger_id, "counter_evidence_ids": item.counter_evidence_ids, "status": item.status, "resolution": item.resolution} for key, item in self.challenges.items()},
            "assessment_reviews": {key: {"id": item.id, "claim_id": item.claim_id, "reviewer_id": item.reviewer_id, "status": item.status, "rationale": item.rationale, "created_at": item.created_at} for key, item in self.assessment_reviews.items()},
            "provenance": [edge.__dict__.copy() for edge in self.provenance.edges],
        }

    def _events_match_audit(self) -> bool:
        if len(self.events) != len(self.audit.events):
            return False
        return all(live.id == audit.event_id and live.event_type == audit.event_type and live.object_id == audit.object_id and live.timestamp == audit.timestamp and live.payload == audit.payload for live, audit in zip(self.events, self.audit.events))

    def verify_state(self) -> bool:
        if not self.verify_history() or not self._events_match_audit():
            return False
        try:
            return self.replay_state() == self.current_state()
        except (KeyError, TypeError, ValueError):
            return False

    def verify(self) -> bool:
        return self.verify_state()
