"""Core domain models for PKL v0.1.

The models deliberately keep evidence dimensions separate instead of
collapsing them into one opaque confidence score.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal
import uuid


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


Status = Literal[
    "proposed",
    "supported",
    "disputed",
    "uncertain",
    "superseded",
    "rejected",
]


@dataclass
class EvidenceProfile:
    methodology_quality: int | None = None
    source_quality: int | None = None
    independence: int | None = None
    replication: int | None = None
    sample_data_strength: int | None = None
    bias_risk: int | None = None
    transparency: int | None = None
    predictive_success: int | None = None
    contradictory_evidence: int | None = None
    relevance: int | None = None
    independence_level: str = "I0"


@dataclass
class Evidence:
    id: str
    claim_id: str
    title: str
    description: str
    source: str | None = None
    contributor_id: str | None = None
    supports_claim: bool | None = None
    profile: EvidenceProfile = field(default_factory=EvidenceProfile)
    created_at: str = field(default_factory=utc_now)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Challenge:
    id: str
    target_id: str
    description: str
    challenger_id: str | None = None
    counter_evidence_ids: list[str] = field(default_factory=list)
    status: str = "open"
    created_at: str = field(default_factory=utc_now)
    resolution: str | None = None


@dataclass
class Assessment:
    status: Status
    evidence_level: str = "E0"
    summary: str = ""
    assessed_at: str = field(default_factory=utc_now)


@dataclass
class Claim:
    id: str
    text: str
    contributor_id: str | None = None
    status: Status = "proposed"
    assessment: Assessment = field(default_factory=Assessment)
    evidence_ids: list[str] = field(default_factory=list)
    challenge_ids: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=utc_now)
    metadata: dict[str, Any] = field(default_factory=dict)



def to_dict(value: Any) -> dict[str, Any]:
    return asdict(value)
