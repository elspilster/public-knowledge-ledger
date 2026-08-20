"""Explicit state-transition rules for replaying PKL audit events."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ReplayState:
    claims: dict[str, dict[str, Any]] = field(default_factory=dict)
    evidence: dict[str, dict[str, Any]] = field(default_factory=dict)
    challenges: dict[str, dict[str, Any]] = field(default_factory=dict)
    provenance: list[dict[str, Any]] = field(default_factory=list)
    keys: dict[str, dict[str, Any]] = field(default_factory=dict)


def apply_event(state: ReplayState, event_type: str, object_id: str, payload: dict[str, Any]) -> None:
    if event_type == "key.registered":
        if object_id in state.keys:
            raise ValueError(f"Key already exists: {object_id}")
        contributor_id = payload["contributor_id"]
        if any(k["contributor_id"] == contributor_id and k["revoked_at_event"] is None for k in state.keys.values()):
            raise ValueError(f"Contributor already has an active key: {contributor_id}")
        state.keys[object_id] = {"contributor_id": contributor_id, "key_id": object_id, "public_key": payload["public_key"], "valid_from_event": payload["valid_from_event"], "revoked_at_event": None, "replaced_by": None}
        return

    if event_type == "key.revoked":
        if object_id not in state.keys:
            raise ValueError(f"Unknown key: {object_id}")
        key = state.keys[object_id]
        if key["revoked_at_event"] is not None:
            raise ValueError(f"Key already revoked: {object_id}")
        replacement = payload.get("replaced_by")
        if replacement is not None and replacement not in state.keys:
            raise ValueError(f"Unknown replacement key: {replacement}")
        key["revoked_at_event"] = payload["revoked_at_event"]
        key["replaced_by"] = replacement
        return

    if event_type == "claim.created":
        if object_id in state.claims:
            raise ValueError(f"Claim already exists: {object_id}")
        state.claims[object_id] = {
            "id": object_id,
            "text": payload["text"],
            "contributor_id": payload.get("contributor_id"),
            "status": "proposed",
            "evidence_level": "E0",
            "summary": "",
        }
        return

    if event_type == "claim.related":
        if object_id not in state.claims or payload["second_id"] not in state.claims:
            raise ValueError("Claim relationship references unknown claim")
        return

    if event_type == "evidence.added":
        if object_id in state.evidence:
            raise ValueError(f"Evidence already exists: {object_id}")
        claim_id = payload["claim_id"]
        if claim_id not in state.claims:
            raise ValueError(f"Evidence references unknown claim: {claim_id}")
        profile = dict(payload.get("profile", {}))
        profile.setdefault("independence_level", "I0")
        state.evidence[object_id] = {
            "id": object_id,
            "claim_id": claim_id,
            "title": payload["title"],
            "description": payload["description"],
            "source": payload.get("source"),
            "contributor_id": payload.get("contributor_id"),
            "supports_claim": payload.get("supports_claim"),
            "profile": profile,
            "metadata": payload.get("metadata", {}),
        }
        return

    if event_type == "evidence.profile_updated":
        if object_id not in state.evidence:
            raise ValueError(f"Profile references unknown evidence: {object_id}")
        state.evidence[object_id]["profile"] = dict(payload["profile"])
        return

    if event_type == "evidence.provenance_linked":
        source_id = payload["source_id"]
        target_id = payload["target_id"]
        if source_id not in state.evidence or target_id not in state.evidence:
            raise ValueError("Provenance link references unknown evidence")
        edge = {"source_id": source_id, "target_id": target_id, "relation": payload["relation"], "note": payload.get("note", "")}
        if edge not in state.provenance:
            state.provenance.append(edge)
        return

    if event_type == "challenge.created":
        if object_id in state.challenges:
            raise ValueError(f"Challenge already exists: {object_id}")
        claim_id = payload["claim_id"]
        if claim_id not in state.claims:
            raise ValueError(f"Challenge references unknown claim: {claim_id}")
        counter_ids = payload.get("counter_evidence_ids", [])
        missing = [eid for eid in counter_ids if eid not in state.evidence]
        if missing:
            raise ValueError(f"Challenge references unknown evidence: {missing}")
        state.challenges[object_id] = {"id": object_id, "target_id": claim_id, "description": payload["description"], "challenger_id": payload.get("challenger_id"), "counter_evidence_ids": counter_ids}
        return

    if event_type == "claim.assessed":
        if object_id not in state.claims:
            raise ValueError(f"Assessment references unknown claim: {object_id}")
        status = payload["status"]
        evidence_level = payload["evidence_level"]
        if status not in {"proposed", "supported", "disputed", "uncertain", "superseded", "rejected", "insufficient_evidence"}:
            raise ValueError(f"Invalid claim status: {status}")
        if evidence_level not in {f"E{i}" for i in range(6)}:
            raise ValueError(f"Invalid evidence level: {evidence_level}")
        state.claims[object_id].update({"status": status, "evidence_level": evidence_level, "summary": payload.get("summary", "")})
        return

    raise ValueError(f"Unknown audit event type: {event_type}")


def replay(events: list[Any]) -> ReplayState:
    state = ReplayState()
    for event in events:
        apply_event(state, event.event_type, event.object_id, event.payload)
    return state
