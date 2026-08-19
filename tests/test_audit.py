from pkl.audit import AuditChain


def test_chain_verifies_when_untouched():
    chain = AuditChain()
    chain.append("EVT-1", "claim.created", "PKL-1", "2026-08-19T12:00:00+00:00", {"text": "Test claim"})
    chain.append("EVT-2", "evidence.added", "EVD-1", "2026-08-19T12:01:00+00:00", {"claim_id": "PKL-1"})

    assert chain.verify() is True


def test_changing_old_payload_is_detected():
    chain = AuditChain()
    chain.append("EVT-1", "claim.created", "PKL-1", "2026-08-19T12:00:00+00:00", {"text": "Test claim"})
    chain.append("EVT-2", "evidence.added", "EVD-1", "2026-08-19T12:01:00+00:00", {"claim_id": "PKL-1"})

    chain.events[0].payload["text"] = "Tampered claim"

    assert chain.verify() is False


def test_deleting_an_event_is_detected():
    chain = AuditChain()
    chain.append("EVT-1", "claim.created", "PKL-1", "2026-08-19T12:00:00+00:00", {"text": "Test claim"})
    chain.append("EVT-2", "evidence.added", "EVD-1", "2026-08-19T12:01:00+00:00", {"claim_id": "PKL-1"})
    chain.append("EVT-3", "claim.assessed", "PKL-1", "2026-08-19T12:02:00+00:00", {"status": "supported"})

    del chain.events[1]

    assert chain.verify() is False


def test_empty_chain_verifies():
    assert AuditChain().verify() is True
