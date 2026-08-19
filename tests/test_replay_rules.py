import pytest

from pkl.replay import ReplayState, apply_event, replay


def test_evidence_cannot_precede_claim():
    state = ReplayState()
    with pytest.raises(ValueError, match="unknown claim"):
        apply_event(state, "evidence.added", "EVD-1", {"claim_id": "PKL-1", "title": "T", "description": "D"})


def test_duplicate_claim_creation_is_rejected():
    state = ReplayState()
    payload = {"text": "Claim"}
    apply_event(state, "claim.created", "PKL-1", payload)
    with pytest.raises(ValueError, match="already exists"):
        apply_event(state, "claim.created", "PKL-1", payload)


def test_assessment_requires_existing_claim():
    state = ReplayState()
    with pytest.raises(ValueError, match="unknown claim"):
        apply_event(state, "claim.assessed", "PKL-1", {"status": "supported", "evidence_level": "E2"})


def test_unknown_event_type_is_rejected():
    with pytest.raises(ValueError, match="Unknown audit event type"):
        replay([type("Event", (), {"event_type": "made.up", "object_id": "X", "payload": {}})()])


def test_valid_sequence_replays():
    state = replay([
        type("Event", (), {"event_type": "claim.created", "object_id": "PKL-1", "payload": {"text": "Claim"}})(),
        type("Event", (), {"event_type": "evidence.added", "object_id": "EVD-1", "payload": {"claim_id": "PKL-1", "title": "T", "description": "D"}})(),
        type("Event", (), {"event_type": "claim.assessed", "object_id": "PKL-1", "payload": {"status": "supported", "evidence_level": "E2", "summary": "OK"}})(),
    ])

    assert state.claims["PKL-1"]["status"] == "supported"
    assert "EVD-1" in state.evidence
