"""Canonical snapshot import/export for PKL ledgers."""

from __future__ import annotations

import json
from typing import Any

from .audit import AuditChain, AuditEvent
from .ledger import Ledger, LedgerEvent
from .models import Assessment, AssessmentReview, Challenge, Claim, Evidence, EvidenceProfile
from .provenance import ProvenanceEdge


def export_ledger(ledger: Ledger) -> str:
    payload: dict[str, Any] = {
        "version": 1,
        "events": [event.__dict__ for event in ledger.events],
        "audit": ledger.audit.snapshot(),
        "claims": {k: _claim(v) for k, v in ledger.claims.items()},
        "evidence": {k: _evidence(v) for k, v in ledger.evidence.items()},
        "challenges": {k: _challenge(v) for k, v in ledger.challenges.items()},
        "assessment_reviews": {k: _assessment_review(v) for k, v in ledger.assessment_reviews.items()},
        "provenance": [edge.__dict__ for edge in ledger.provenance.edges],
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def import_ledger(data: str) -> Ledger:
    raw = json.loads(data)
    if raw.get("version") != 1:
        raise ValueError("Unsupported ledger snapshot version")
    ledger = Ledger()
    ledger.events = [LedgerEvent(**item) for item in raw["events"]]
    ledger.audit.events = [AuditEvent(**item) for item in raw["audit"]]
    ledger.claims = {k: _claim_from(v) for k, v in raw["claims"].items()}
    ledger.evidence = {k: _evidence_from(v) for k, v in raw["evidence"].items()}
    ledger.challenges = {k: _challenge_from(v) for k, v in raw["challenges"].items()}
    ledger.assessment_reviews = {k: _assessment_review_from(v) for k, v in raw.get("assessment_reviews", {}).items()}
    for edge in raw.get("provenance", []):
        ledger.provenance.edges.append(ProvenanceEdge(**edge))
    if not ledger.verify():
        raise ValueError("Ledger snapshot failed integrity verification")
    return ledger


def _claim(c: Claim) -> dict[str, Any]:
    return {
        "id": c.id,
        "text": c.text,
        "contributor_id": c.contributor_id,
        "status": c.status,
        "assessment": c.assessment.__dict__,
        "evidence_ids": c.evidence_ids,
        "challenge_ids": c.challenge_ids,
        "assessment_history": c.assessment_history,
        "assessment_review_ids": c.assessment_review_ids,
        "created_at": c.created_at,
        "metadata": c.metadata,
    }


def _evidence(e: Evidence) -> dict[str, Any]:
    return {"id": e.id, "claim_id": e.claim_id, "title": e.title, "description": e.description, "source": e.source, "contributor_id": e.contributor_id, "supports_claim": e.supports_claim, "profile": e.profile.as_dict(), "created_at": e.created_at, "metadata": e.metadata}


def _challenge(c: Challenge) -> dict[str, Any]:
    return c.__dict__.copy()


def _assessment_review(review: AssessmentReview) -> dict[str, Any]:
    return {
        "id": review.id,
        "claim_id": review.claim_id,
        "reviewer_id": review.reviewer_id,
        "status": review.status,
        "rationale": review.rationale,
        "created_at": review.created_at,
    }


def _claim_from(v: dict[str, Any]) -> Claim:
    return Claim(
        id=v["id"],
        text=v["text"],
        contributor_id=v["contributor_id"],
        status=v["status"],
        assessment=Assessment(**v["assessment"]),
        evidence_ids=list(v["evidence_ids"]),
        challenge_ids=list(v["challenge_ids"]),
        assessment_history=list(v.get("assessment_history", [])),
        assessment_review_ids=list(v.get("assessment_review_ids", [])),
        created_at=v["created_at"],
        metadata=dict(v["metadata"]),
    )


def _evidence_from(v: dict[str, Any]) -> Evidence:
    return Evidence(v["id"], v["claim_id"], v["title"], v["description"], v["source"], v["contributor_id"], v["supports_claim"], EvidenceProfile(**v["profile"]), v["created_at"], dict(v["metadata"]))


def _challenge_from(v: dict[str, Any]) -> Challenge:
    return Challenge(v["id"], v["target_id"], v["description"], v["challenger_id"], list(v["counter_evidence_ids"]), v["status"], v["created_at"], v["resolution"])


def _assessment_review_from(v: dict[str, Any]) -> AssessmentReview:
    return AssessmentReview(
        id=v["id"],
        claim_id=v["claim_id"],
        reviewer_id=v["reviewer_id"],
        status=v["status"],
        rationale=v["rationale"],
        created_at=v["created_at"],
    )
