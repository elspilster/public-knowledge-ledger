from pkl import Ledger


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
