from pkl import Ledger


def make_ledger():
    ledger = Ledger()
    claim = ledger.create_claim("Original claim", contributor_id="human-1")
    ledger.add_evidence(claim.id, "Evidence", "Description", source="source-1", supports_claim=True)
    ledger.challenge_claim(claim.id, "Challenge", challenger_id="human-2")
    ledger.assess_claim(claim.id, "supported", evidence_level="E2", summary="Supported for now")
    return ledger, claim


def test_live_state_matches_replayed_history():
    ledger, _ = make_ledger()
    assert ledger.verify_state() is True
    assert ledger.verify() is True


def test_unaudited_live_state_change_is_detected():
    ledger, claim = make_ledger()
    claim.text = "Secretly altered claim"

    assert ledger.verify_history() is True
    assert ledger.verify_state() is False
    assert ledger.verify() is False


def test_unaudited_new_claim_is_detected():
    ledger, _ = make_ledger()
    rogue = ledger.create_claim("Rogue claim")
    # Simulate state mutation without its audit event.
    ledger.audit.events.pop()
    assert rogue.id in ledger.claims
    assert ledger.verify() is False


def test_audit_tampering_is_detected_before_state_comparison():
    ledger, _ = make_ledger()
    ledger.audit.events[0].payload["text"] = "Tampered history"
    assert ledger.verify() is False
