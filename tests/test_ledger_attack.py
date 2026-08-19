from copy import deepcopy

from pkl import Ledger


def populated_ledger():
    ledger = Ledger()
    claim = ledger.create_claim("Original claim")
    ledger.add_evidence(claim.id, "Evidence", "Description")
    ledger.assess_claim(claim.id, "supported", evidence_level="E2")
    return ledger


def test_reordering_audit_events_is_detected():
    ledger = populated_ledger()
    ledger.audit.events[0], ledger.audit.events[1] = ledger.audit.events[1], ledger.audit.events[0]
    assert ledger.verify_history() is False


def test_forged_event_is_detected():
    ledger = populated_ledger()
    forged = deepcopy(ledger.audit.events[-1])
    ledger.audit.events.append(forged)
    assert ledger.verify_history() is False


def test_deleting_audit_event_is_detected():
    ledger = populated_ledger()
    del ledger.audit.events[1]
    assert ledger.verify_history() is False


def test_changing_audit_payload_is_detected():
    ledger = populated_ledger()
    ledger.audit.events[0].payload["text"] = "Forged claim"
    assert ledger.verify_history() is False


def test_normal_ledger_history_and_audit_history_agree():
    ledger = populated_ledger()
    assert len(ledger.events) == len(ledger.audit.events)
    assert [event.id for event in ledger.events] == [event.event_id for event in ledger.audit.events]
    assert ledger.verify_history() is True


def test_mutating_current_state_does_not_fake_audit_history():
    ledger = populated_ledger()
    claim = next(iter(ledger.claims.values()))
    claim.text = "State changed without an audit event"

    # The audit chain remains internally valid, but it cannot be mistaken for
    # proof that the current state still matches the audited history.
    assert ledger.verify_history() is True
    assert ledger.audit.events[0].payload["text"] == "Original claim"
