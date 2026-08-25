from datetime import datetime, timezone

from pkl.api import SubmissionAPI
from pkl.submissions import SubmissionStore


def make_api(tmp_path):
    return SubmissionAPI(
        SubmissionStore(tmp_path / "submissions.json", max_per_window=2),
        reviewer_token="review-secret",
    )


def test_submission_review_acceptance_and_public_projection(tmp_path):
    api = make_api(tmp_path)
    status, body = api.submit(
        {
            "title": "A test claim",
            "statement": "A test statement.",
            "category": "Testing",
            "evidence": ["source one"],
        },
        contributor_id="human-1",
    )
    assert status == 201
    submission_id = body["submission"]["id"]

    status, body = api.public_submissions()
    assert status == 200
    assert body["submissions"] == []

    status, body = api.reviewer_queue("wrong")
    assert status == 401
    assert body["error"] == "reviewer authentication required"

    status, body = api.reviewer_queue("review-secret")
    assert status == 200
    assert body["submissions"][0]["id"] == submission_id
    assert body["submissions"][0]["contributor_id"] == "human-1"

    status, body = api.moderate(
        submission_id,
        {"status": "accepted", "reviewer_id": "reviewer-1", "note": "Evidence checked."},
        "review-secret",
    )
    assert status == 200
    assert body["submission"]["status"] == "accepted"

    status, body = api.public_submissions()
    assert status == 200
    assert body["submissions"][0]["id"] == submission_id
    assert "contributor_id" not in body["submissions"][0]
    assert "review_note" not in body["submissions"][0]


def test_rejected_submission_never_enters_public_projection(tmp_path):
    api = make_api(tmp_path)
    status, body = api.submit(
        {"title": "Reject me", "statement": "Not public", "category": "Test"},
        contributor_id="human-2",
    )
    submission_id = body["submission"]["id"]
    status, _ = api.moderate(
        submission_id,
        {"status": "rejected", "reviewer_id": "reviewer-1"},
        "review-secret",
    )
    assert status == 200
    assert api.public_submissions()[1]["submissions"] == []


def test_duplicate_and_rate_limit_errors_are_stable(tmp_path):
    api = make_api(tmp_path)
    payload = {"title": "Same", "statement": "Same statement", "category": "Test"}
    assert api.submit(payload, contributor_id="ai-1")[0] == 201
    assert api.submit(payload, contributor_id="ai-2")[0] == 409

    assert api.submit({"title": "Two", "statement": "Two", "category": "Test"}, contributor_id="ai-1")[0] == 201
    assert api.submit({"title": "Three", "statement": "Three", "category": "Test"}, contributor_id="ai-1")[0] == 429


def test_invalid_transition_and_missing_reviewer_are_rejected(tmp_path):
    api = make_api(tmp_path)
    status, body = api.submit(
        {"title": "Transition", "statement": "Test", "category": "Test"},
        contributor_id="human-3",
    )
    submission_id = body["submission"]["id"]

    assert api.moderate(submission_id, {"status": "accepted", "reviewer_id": ""}, "review-secret")[0] == 400
    assert api.moderate(submission_id, {"status": "pending_review", "reviewer_id": "r"}, "review-secret")[0] == 409
    assert api.moderate("missing", {"status": "accepted", "reviewer_id": "r"}, "review-secret")[0] == 404


def test_persistence_survives_new_api_instance(tmp_path):
    path = tmp_path / "submissions.json"
    store = SubmissionStore(path)
    fixed = datetime(2026, 1, 1, tzinfo=timezone.utc)
    item = store.submit(
        title="Persistent",
        statement="This survives reload",
        category="Testing",
        contributor_id="human-4",
        now=fixed,
    )
    store.moderate(item.id, status="accepted", reviewer_id="reviewer-1", now=fixed)

    reloaded = SubmissionAPI(SubmissionStore(path), reviewer_token="review-secret")
    status, body = reloaded.public_submissions()
    assert status == 200
    assert body["submissions"][0]["id"] == item.id
