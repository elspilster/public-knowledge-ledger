from pkl import Ledger
from pkl.audit import calculate_hash


def test_ledger_operations_are_audited():
    ledger = Ledger()
    claim = ledger.create_claim("Test claim")
    ledger.add_evidence(claim.id, "Evidence", "Description")
    ledger.challenge_claim(claim.id, "Challenge")
    ledger.assess_claim(claim.id, "uncertain", evidence_level="E1")

    assert ledger.verify_history() is True
    assert len(ledger.events) == 4
    assert len(ledger.audit.events) == 4


def test_tampering_with_ledger_history_is_detected():
    ledger = Ledger()
    claim = ledger.create_claim("Original claim")
    ledger.assess_claim(claim.id, "supported", evidence_level="E2")

    ledger.audit.events[0].payload["text"] = "Altered claim"

    assert ledger.verify_history() is False


def test_correction_event_tampering_is_detected():
    ledger = Ledger()
    claim = ledger.create_claim("Original wording")
    ledger.correct_claim(claim.id, "Corrected wording", reason="Clarified scope")

    ledger.audit.events[-1].payload["new_text"] = "Silently altered wording"

    assert ledger.verify_history() is False


def test_canonical_hash_is_deterministic_for_m3_event_payloads():
    payload_a = {
        "old_text": "Version one",
        "new_text": "Version two",
        "reason": "Clarified scope",
    }
    payload_b = {
        "reason": "Clarified scope",
        "new_text": "Version two",
        "old_text": "Version one",
    }

    first = calculate_hash("EVT-1", "claim.corrected", "PKL-1", "2026-08-20T00:00:00+00:00", payload_a, "0" * 64)
    second = calculate_hash("EVT-1", "claim.corrected", "PKL-1", "2026-08-20T00:00:00+00:00", payload_b, "0" * 64)

    assert first == second


def test_m3_correction_history_remains_replayable_after_multiple_corrections():
    ledger = Ledger()
    claim = ledger.create_claim("Version one")
    ledger.correct_claim(claim.id, "Version two", reason="First clarification")
    ledger.correct_claim(claim.id, "Version three", reason="Second clarification")

    history = ledger.history(claim.id)
    assert history[0].payload["text"] == "Version one"
    assert history[1].payload["new_text"] == "Version two"
    assert history[2].payload["new_text"] == "Version three"
    assert ledger.replay_state() == ledger.current_state()
    assert ledger.verify_history()
