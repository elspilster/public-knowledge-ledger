"""HTTP-facing service adapter for PKL submissions."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .submissions import SubmissionError, SubmissionStore


class SubmissionAPI:
    """Dependency-free API adapter with stable public/reviewer boundaries."""

    def __init__(self, store: SubmissionStore, *, reviewer_token: str | None = None):
        self.store = store
        self.reviewer_token = reviewer_token

    @staticmethod
    def _submission(item: Any, *, include_private: bool = False) -> dict[str, Any]:
        data = asdict(item)
        data.pop("rate_limit_id", None)
        if not include_private:
            data.pop("contributor_id", None)
            data.pop("review_note", None)
            data.pop("reviewed_at", None)
        return data

    def _auth(self, token: str | None) -> tuple[bool, dict[str, Any] | None]:
        if not self.reviewer_token:
            return False, {"error": "reviewer API is not configured"}
        if token != self.reviewer_token:
            return False, {"error": "reviewer authentication required"}
        return True, None

    def public_submissions(self) -> tuple[int, dict[str, Any]]:
        return 200, {"submissions": [self._submission(item) for item in self.store.public()]}

    def submit(
        self,
        payload: dict[str, Any],
        *,
        contributor_id: str | None,
        rate_limit_id: str | None = None,
    ) -> tuple[int, dict[str, Any]]:
        try:
            item = self.store.submit(
                title=str(payload.get("title", "")),
                statement=str(payload.get("statement", "")),
                category=str(payload.get("category", "")),
                evidence=_strings(payload.get("evidence")),
                limitations=_strings(payload.get("limitations")),
                relationships=_strings(payload.get("relationships")),
                contributor_id=contributor_id,
                rate_limit_id=rate_limit_id,
            )
        except SubmissionError as exc:
            message = str(exc)
            if "duplicate" in message:
                return 409, {"error": message, "code": "duplicate"}
            if "rate limit" in message:
                return 429, {"error": message, "code": "rate_limit"}
            return 400, {"error": message, "code": "validation"}
        return 201, {"submission": self._submission(item, include_private=True)}

    def reviewer_queue(self, token: str | None) -> tuple[int, dict[str, Any]]:
        ok, error = self._auth(token)
        if not ok:
            return 401 if self.reviewer_token else 503, error or {"error": "unauthorized"}
        return 200, {"submissions": [self._submission(item, include_private=True) for item in self.store.pending()]}

    def reviewer_audit(self, token: str | None) -> tuple[int, dict[str, Any]]:
        ok, error = self._auth(token)
        if not ok:
            return 401 if self.reviewer_token else 503, error or {"error": "unauthorized"}
        return 200, {"audit": self.store.audit_log()}

    def moderate(self, submission_id: str, payload: dict[str, Any], token: str | None) -> tuple[int, dict[str, Any]]:
        ok, error = self._auth(token)
        if not ok:
            return 401 if self.reviewer_token else 503, error or {"error": "unauthorized"}
        try:
            item = self.store.moderate(
                submission_id,
                status=str(payload.get("status", "")),
                reviewer_id=str(payload.get("reviewer_id", "")),
                note=str(payload.get("note", "")),
            )
        except SubmissionError as exc:
            message = str(exc)
            if "not found" in message:
                return 404, {"error": message, "code": "not_found"}
            if "only pending" in message or "invalid moderation" in message:
                return 409, {"error": message, "code": "invalid_transition"}
            return 400, {"error": message, "code": "validation"}
        return 200, {"submission": self._submission(item, include_private=True)}


def _strings(value: Any) -> list[str]:
    if value is None or value == "":
        return []
    if isinstance(value, str):
        return [line.strip() for line in value.splitlines() if line.strip()]
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    raise SubmissionError("evidence, limitations, and relationships must be strings or lists")
