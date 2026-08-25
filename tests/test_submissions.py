from datetime import datetime, timedelta, timezone

import pytest

from pkl.submissions import SubmissionError, SubmissionStore


def test_submission_persists_as_pending_and_only_accepted_is_public(tmp_path):
    path = tmp_path / "submissions.json"
    store = SubmissionStore(path)
    created = store.submit(
        title="A test claim",
        statement="A precise statement",
        category="Testing",
        contributor_id="alice",
    )

    assert created.status == "pending_review"
    assert store.pending()[0].id == created.id
    assert store.public() == []

    reloaded = SubmissionStore(path)
    assert reloaded.get(created.id).status == "pending_review"
    reloaded.moderate(created.id, status="accepted", reviewer_id="reviewer-1", note="Evidence reviewed")
    assert [item.id for item in reloaded.public()] == [created.id]


def test_duplicate_submissions_are_rejected(tmp_path):
    store = SubmissionStore(tmp_path / "submissions.json")
    kwargs = dict(title="Same", statement="Same statement", category="Science", contributor_id="alice")
    store.submit(**kwargs)
    with pytest.raises(SubmissionError, match="duplicate"):
        store.submit(**kwargs)


def test_rate_limit_is_per_contributor_and_time_window(tmp_path):
    store = SubmissionStore(tmp_path / "submissions.json", max_per_window=2, window_seconds=3600)
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    store.submit(title="One", statement="One statement", category="A", contributor_id="alice", now=now)
    store.submit(title="Two", statement="Two statement", category="A", contributor_id="alice", now=now + timedelta(minutes=1))
    with pytest.raises(SubmissionError, match="rate limit"):
        store.submit(title="Three", statement="Three statement", category="A", contributor_id="alice", now=now + timedelta(minutes=2))

    # A different contributor is not blocked by Alice's quota.
    store.submit(title="Other", statement="Other statement", category="A", contributor_id="bob", now=now + timedelta(minutes=2))


def test_invalid_moderation_transitions_are_rejected(tmp_path):
    store = SubmissionStore(tmp_path / "submissions.json")
    created = store.submit(title="Claim", statement="Statement", category="Category")

    with pytest.raises(SubmissionError, match="reviewer_id"):
        store.moderate(created.id, status="accepted", reviewer_id="")

    store.moderate(created.id, status="rejected", reviewer_id="reviewer")
    with pytest.raises(SubmissionError, match="only pending"):
        store.moderate(created.id, status="accepted", reviewer_id="reviewer")


def test_audit_log_records_submission_and_moderation(tmp_path):
    store = SubmissionStore(tmp_path / "submissions.json")
    created = store.submit(title="Claim", statement="Statement", category="Category")
    store.moderate(created.id, status="accepted", reviewer_id="reviewer")

    assert [entry["action"] for entry in store.audit_log()] == ["submitted", "accepted"]
    assert store.audit_log()[-1]["reviewer_id"] == "reviewer"
