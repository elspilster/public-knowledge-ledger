"""Explainable queries over claims, evidence, provenance and council decisions."""

from __future__ import annotations

from typing import Any

from .council import RootCouncil
from .ledger import Ledger
from .provenance import ProvenanceGraph


class KnowledgeQuery:
    def __init__(self, ledger: Ledger, provenance: ProvenanceGraph | None = None, council: RootCouncil | None = None) -> None:
        self.ledger = ledger
        self.provenance = provenance or ledger.provenance
        self.council = council

    def explain(self, claim_id: str) -> dict[str, Any]:
        claim = self.ledger.get_claim(claim_id)
        evidence = [self.ledger.evidence[eid] for eid in claim.evidence_ids]
        challenges = [self.ledger.challenges[cid] for cid in claim.challenge_ids]
        council_decision = self.council.latest(claim_id) if self.council else None
        provenance = {
            item.id: [edge.__dict__ for edge in self.provenance.related(item.id)]
            for item in evidence
        }
        return {
            "claim": {
                "id": claim.id,
                "text": claim.text,
                "contributor_id": claim.contributor_id,
                "status": claim.status,
                "assessment": {
                    "evidence_level": claim.assessment.evidence_level,
                    "summary": claim.assessment.summary,
                    "supporting_evidence_ids": list(claim.assessment.supporting_evidence_ids),
                    "contradicting_evidence_ids": list(claim.assessment.contradicting_evidence_ids),
                    "limitations": list(claim.assessment.limitations),
                    "assessed_at": claim.assessment.assessed_at,
                },
            },
            "evidence": [
                {
                    "id": item.id,
                    "title": item.title,
                    "description": item.description,
                    "source": item.source,
                    "contributor_id": item.contributor_id,
                    "supports_claim": item.supports_claim,
                    "independence_level": item.profile.independence_level,
                    "provenance": provenance[item.id],
                }
                for item in evidence
            ],
            "challenges": [
                {
                    "id": item.id,
                    "description": item.description,
                    "challenger_id": item.challenger_id,
                    "counter_evidence_ids": list(item.counter_evidence_ids),
                    "status": item.status,
                    "resolution": item.resolution,
                }
                for item in challenges
            ],
            "council": None if council_decision is None else {
                "id": council_decision.id,
                "decision": council_decision.decision,
                "signers": sorted(council_decision.signers),
                "rationale": council_decision.rationale,
                "created_at": council_decision.created_at,
            },
            "assessment_reviews": [
                {
                    "id": review.id,
                    "reviewer_id": review.reviewer_id,
                    "position": review.position,
                    "rationale": review.rationale,
                    "created_at": review.created_at,
                }
                for review in (self.ledger.assessment_reviews[rid] for rid in claim.assessment_review_ids)
            ],
            "authenticated_is_not_true": True,
            "history": [event.__dict__ for event in self.ledger.history(claim_id)],
        }

    def search(self, text: str, *, limit: int = 50) -> list[dict[str, Any]]:
        needle = text.strip().lower()
        if not needle:
            return []
        if limit < 1:
            raise ValueError("limit must be at least 1")
        return [
            {"id": claim.id, "text": claim.text, "status": claim.status}
            for claim in self.ledger.claims.values()
            if needle in claim.text.lower()
        ][:limit]
