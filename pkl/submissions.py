"""Submission and moderation primitives for the public PKL surface.

A submission is a proposal, never a published knowledge record. This module
keeps the persistence boundary deliberately small and dependency-free so it
can sit behind an HTTP/API layer without changing moderation rules.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import tempfile
from typing import Literal
import uuid


SubmissionStatus = Literal["pending_review", "accepted", "rejected", "withdrawn"]


class SubmissionError(ValueError):
    """Raised when a submission or moderation transition is invalid."""


@dataclass
class Submission:
    id: str
    title: str
    statement: str
    category: str
    evidence: list[str] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    relationships: list[str] = field(default_factory=list)
    contributor_id: str | None = None
    status: SubmissionStatus = "pending_review"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    reviewed_at: str | None = None
    review_note: str | None = None

    @property
    def fingerprint(self) -> str:
        payload = "\n".join(_normalise(value) for value in (self.title, self.statement, self.category))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _normalise(value: str) -> str:
    return " ".join(value.strip().casefold().split())


class SubmissionStore:
    """Small JSON-backed store with validation, duplicate and rate controls."""

    def __init__(self, path: str | Path, *, max_per_window: int = 5, window_seconds: int = 3600):
        self.path = Path(path)
        self.max_per_window = max_per_window
        self.window = timedelta(seconds=window_seconds)
        self._submissions: list[Submission] = []
        self._audit: list[dict[str, str]] = []
        self.load()

    def load(self) -> None:
        if not self.path.exists():
            self._submissions = []
            self._audit = []
            return
        data = json.loads(self.path.read_text(encoding="utf-8"))
        self._submissions = [Submission(**item) for item in data.get("submissions", [])]
        self._audit = list(data.get("audit", []))

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"submissions": [asdict(item) for item in self._submissions], "audit": self._audit}
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=self.path.parent, delete=False) as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
            temp_path = Path(handle.name)
        temp_path.replace(self.path)

    def _validate(self, title: str, statement: str, category: str) -> None:
        if not _normalise(title) or not _normalise(statement) or not _normalise(category):
            raise SubmissionError("title, statement, and category are required")
        if len(title.strip()) > 240:
            raise SubmissionError("title is too long")
        if len(statement.strip()) > 10000:
            raise SubmissionError("statement is too long")
        if len(category.strip()) > 120:
            raise SubmissionError("category is too long")

    def submit(
        self,
        *,
        title: str,
        statement: str,
        category: str,
        evidence: list[str] | None = None,
        limitations: list[str] | None = None,
        relationships: list[str] | None = None,
        contributor_id: str | None = None,
        rate_limit_id: str | None = None,
        now: datetime | None = None,
    ) -> Submission:
        self._validate(title, statement, category)
        now = now or datetime.now(timezone.utc)
        contributor = contributor_id or "anonymous"
        limiter = rate_limit_id or contributor
        cutoff = now - self.window
        recent = [
            item for item in self._submissions
            if (item.contributor_id or "anonymous") == contributor
            and datetime.fromisoformat(item.created_at) >= cutoff
            and (item.__dict__.get("_rate_limit_id", limiter) == limiter)
        ]
        if len(recent) >= self.max_per_window:
            raise SubmissionError("submission rate limit exceeded")

        candidate = Submission(
            id=f"PKL-SUB-{uuid.uuid4().hex[:12]}",
            title=title.strip(),
            statement=statement.strip(),
            category=category.strip(),
            evidence=[item.strip() for item in (evidence or []) if item.strip()],
            limitations=[item.strip() for item in (limitations or []) if item.strip()],
            relationships=[item.strip() for item in (relationships or []) if item.strip()],
            contributor_id=contributor_id,
            created_at=now.isoformat(),
        )
        object.__setattr__(candidate, "_rate_limit_id", limiter)
        if any(item.fingerprint == candidate.fingerprint for item in self._submissions):
            raise SubmissionError("duplicate submission")

        self._submissions.append(candidate)
        self._audit.append({"action": "submitted", "submission_id": candidate.id, "at": candidate.created_at})
        self._save()
        return candidate

    def moderate(self, submission_id: str, *, status: SubmissionStatus, reviewer_id: str, note: str = "", now: datetime | None = None) -> Submission:
        if status not in {"accepted", "rejected", "withdrawn"}:
            raise SubmissionError("invalid moderation status")
        if not reviewer_id.strip():
            raise SubmissionError("reviewer_id is required")
        submission = self.get(submission_id)
        if submission.status != "pending_review":
            raise SubmissionError("only pending submissions can be moderated")
        now = now or datetime.now(timezone.utc)
        submission.status = status
        submission.reviewed_at = now.isoformat()
        submission.review_note = note.strip() or None
        self._audit.append({"action": status, "submission_id": submission.id, "reviewer_id": reviewer_id, "at": submission.reviewed_at})
        self._save()
        return submission

    def withdraw(self, submission_id: str, *, now: datetime | None = None) -> Submission:
        submission = self.get(submission_id)
        if submission.status != "pending_review":
            raise SubmissionError("only pending submissions can be withdrawn")
        now = now or datetime.now(timezone.utc)
        submission.status = "withdrawn"
        submission.reviewed_at = now.isoformat()
        self._audit.append({"action": "withdrawn", "submission_id": submission.id, "at": submission.reviewed_at})
        self._save()
        return submission

    def get(self, submission_id: str) -> Submission:
        for submission in self._submissions:
            if submission.id == submission_id:
                return submission
        raise SubmissionError("submission not found")

    def pending(self) -> list[Submission]:
        return [item for item in self._submissions if item.status == "pending_review"]

    def public(self) -> list[Submission]:
        return [item for item in self._submissions if item.status == "accepted"]

    def audit_log(self) -> list[dict[str, str]]:
        return list(self._audit)
