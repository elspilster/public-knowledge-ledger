"""Core domain models for PKL v0.1."""

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
    "proposed", "supported", "disputed", "uncertain", "superseded", "rejected"
]

INDEPENDENCE_LEVELS = {f"I{i}" for i in range(5)}
PROFILE_DIMENSIONS = (
    "methodology_quality", "source_quality", "independence", "replication",
    "sample_data_strength", "bias_risk", "transparency", "predictive_success",
    "contradictory_evidence", "relevance",
)


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

    def validate(self) -> None:
        for name in PROFILE_DIMENSIONS:
            value = getattr(self, name)
            if value is not None and not isinstance(value, int):
                raise ValueError(f"{name} must be an integer from 0 to 5 or None")
            if value is not None and not 0 <= value <= 5:
                raise ValueError(f"{name} must be between 0 and 5")
        if self.independence_level not in INDEPENDENCE_LEVELS:
            raise ValueError(f"Invalid independence level: {self.independence_level}")

    def as_dict(self) -> dict[str, Any]:
        self.validate()
        return asdict(self)


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
    status: Status = "proposed"
    evidence_level: str = "E0"
    summary: str = ""
    assessed_at: str = field(default_factory=utc_now)


@dataclass(frozen=True)
class AssessmentReview:
    id: str
    claim_id: str
    reviewer_id: str
    status: Status
    rationale: str
    created_at: str = field(default_factory=utc_now)


@dataclass
class Claim:
    id: str
    text: str
    contributor_id: str | None = None
    status: Status = "proposed"
    assessment: Assessment = field(default_factory=Assessment)
    evidence_ids: list[str] = field(default_factory=list)
    challenge_ids: list[str] = field(default_factory=list)
    assessment_history: list[dict[str, Any]] = field(default_factory=list)
    assessment_review_ids: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=utc_now)
    metadata: dict[str, Any] = field(default_factory=dict)


def to_dict(value: Any) -> dict[str, Any]:
    return asdict(value)
