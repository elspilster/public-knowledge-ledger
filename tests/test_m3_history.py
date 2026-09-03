from pkl import Ledger


def test_correction_preserves_original_claim_event():
    ledger = Ledger()
    claim = ledger.create_claim("Original wording")
    ledger.correct_claim(claim.id, "Corrected wording", reason="New evidence")

    history = ledger.history(claim.id)
    assert history[0].event_type == "claim.created"
    assert history[0].payload["text"] == "Original wording"
    assert history[-1].event_type == "claim.corrected"
    assert claim.text == "Corrected wording"


def test_correction_replay_reconstructs_current_state():
    ledger = Ledger()
    claim = ledger.create_claim("Original")
    ledger.correct_claim(claim.id, "Corrected", reason="Correction")
    assert ledger.verify()
    assert ledger.replay_state()["claims"][claim.id]["text"] == "Corrected"


def test_challenge_can_be_resolved_only_once():
    ledger = Ledger()
    claim = ledger.create_claim("A claim")
    challenge = ledger.challenge_claim(claim.id, "Counterargument", challenger_id="reviewer")
    ledger.resolve_challenge(challenge.id, "Evidence did not support the challenge", resolver_id="reviewer-2")

    assert challenge.status == "resolved"
    assert challenge.resolution == "Evidence did not support the challenge"
    try:
        ledger.resolve_challenge(challenge.id, "Second resolution")
    except ValueError:
        pass
    else:
        raise AssertionError("A resolved challenge must not be resolved twice")


def test_assessment_history_preserves_each_transition():
    ledger = Ledger()
    claim = ledger.create_claim("A claim")
    ledger.assess_claim(claim.id, "uncertain", evidence_level="E1", summary="Initial assessment")
    ledger.assess_claim(claim.id, "supported", evidence_level="E2", summary="New evidence")

    assert [item["status"] for item in claim.assessment_history] == ["uncertain", "supported"]
    assert len(ledger.history(claim.id)) == 3
    assert ledger.verify()


def test_reviewer_disagreement_is_retained():
    ledger = Ledger()
    claim = ledger.create_claim("A claim")
    first = ledger.review_assessment(claim.id, "reviewer-a", "supported", rationale="Strong evidence")
    second = ledger.review_assessment(claim.id, "reviewer-b", "disputed", rationale="Important contradiction")

    assert first.status == "supported"
    assert second.status == "disputed"
    assert claim.assessment_review_ids == [first.id, second.id]
    assert ledger.replay_state()["assessment_reviews"][second.id]["status"] == "disputed"


def test_tampering_with_m3_event_breaks_verification():
    ledger = Ledger()
    claim = ledger.create_claim("Original")
    ledger.correct_claim(claim.id, "Corrected", reason="Reason")
    ledger.events[-1].payload["corrected_text"] = "Tampered"
    assert ledger.verify() is False
