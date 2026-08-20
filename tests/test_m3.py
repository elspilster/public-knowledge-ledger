import pytest

from pkl import Ledger


def test_assessment_history_survives_multiple_transitions_and_replay():
    ledger = Ledger()
    claim = ledger.create_claim("Initial claim")

    ledger.assess_claim(claim.id, "uncertain", evidence_level="E1", summary="Initial evidence is limited.")
    ledger.assess_claim(claim.id, "supported", evidence_level="E3", summary="Additional independent support was recorded.")
    ledger.assess_claim(claim.id, "disputed", evidence_level="E1", summary="A material contradiction was recorded.")

    assert [item.status for item in claim.assessment_history] == ["uncertain", "supported", "disputed"]
    assert ledger.current_state()["claims"][claim.id]["status"] == "disputed"
    assert len(ledger.current_state()["claims"][claim.id]["assessment_history"]) == 3
    assert ledger.replay_state() == ledger.current_state()
    assert ledger.verify()


def test_correction_changes_current_text_without_erasing_original_event():
    ledger = Ledger()
    claim = ledger.create_claim("The original wording.")

    ledger.correct_claim(claim.id, "The corrected wording.", reason="The original wording overstated the evidence.")

    assert claim.text == "The corrected wording."
    history = ledger.history(claim.id)
    assert [event.event_type for event in history] == ["claim.created", "claim.corrected"]
    assert history[0].payload["text"] == "The original wording."
    assert history[1].payload["old_text"] == "The original wording."
    assert history[1].payload["new_text"] == "The corrected wording."
    assert ledger.verify()


def test_correction_cannot_erase_history_and_replay_matches_current_state():
    ledger = Ledger()
    claim = ledger.create_claim("Version one")
    ledger.correct_claim(claim.id, "Version two", reason="New information changed the wording.")
    ledger.correct_claim(claim.id, "Version three", reason="A second correction clarified scope.")

    events = ledger.history(claim.id)
    assert [event.payload.get("new_text") for event in events[1:]] == ["Version two", "Version three"]
    assert events[0].payload["text"] == "Version one"
    assert ledger.replay_state() == ledger.current_state()


def test_challenge_can_remain_open_or_be_resolved():
    ledger = Ledger()
    claim = ledger.create_claim("A claim that may be challenged")
    open_challenge = ledger.challenge_claim(claim.id, "The evidence is incomplete.", challenger_id="reviewer-a")
    resolved_challenge = ledger.challenge_claim(claim.id, "A source contradicts this.", challenger_id="reviewer-b")

    ledger.resolve_challenge(resolved_challenge.id, "The contradiction was addressed by the later evidence.")

    assert ledger.challenges[open_challenge.id].status == "open"
    assert ledger.challenges[resolved_challenge.id].status == "resolved"
    assert ledger.challenges[resolved_challenge.id].resolution
    assert ledger.replay_state() == ledger.current_state()
    assert ledger.verify()


def test_resolving_a_challenge_twice_is_rejected_without_extra_history():
    ledger = Ledger()
    claim = ledger.create_claim("Claim")
    challenge = ledger.challenge_claim(claim.id, "Challenge")
    ledger.resolve_challenge(challenge.id, "Resolved with additional evidence.")
    event_count = len(ledger.events)

    with pytest.raises(ValueError, match="already resolved"):
        ledger.resolve_challenge(challenge.id, "Attempted second resolution")

    assert len(ledger.events) == event_count
    assert ledger.verify()


def test_reviewer_disagreement_is_preserved():
    ledger = Ledger()
    claim = ledger.create_claim("Assessment subject")
    ledger.assess_claim(claim.id, "supported", evidence_level="E3", summary="Two recorded evidence families support it.")

    first = ledger.record_assessment_review(claim.id, "reviewer-a", "supported", "The supporting evidence is relevant.")
    second = ledger.record_assessment_review(claim.id, "reviewer-b", "disputed", "A material contradiction remains unresolved.")

    assert claim.assessment_review_ids == [first.id, second.id]
    assert ledger.assessment_reviews[second.id].position == "disputed"
    assert ledger.current_state()["claims"][claim.id]["status"] == "supported"
    assert ledger.replay_state() == ledger.current_state()
    assert ledger.verify()


def test_m3_events_are_replayable_end_to_end():
    ledger = Ledger()
    claim = ledger.create_claim("Initial claim")
    ledger.assess_claim(claim.id, "uncertain", evidence_level="E1", summary="Initial uncertainty.")
    challenge = ledger.challenge_claim(claim.id, "Needs a correction.")
    ledger.correct_claim(claim.id, "Corrected claim", reason="Clarified scope after challenge.")
    ledger.resolve_challenge(challenge.id, "Correction accepted; challenge resolved.")
    ledger.assess_claim(claim.id, "disputed", evidence_level="E2", summary="The correction exposed a remaining disagreement.")
    ledger.record_assessment_review(claim.id, "reviewer-a", "disputed", "The disagreement remains material.")

    assert ledger.verify_history()
    assert ledger.replay_state() == ledger.current_state()
    assert ledger.verify()
