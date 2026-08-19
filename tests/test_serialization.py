import json

import pytest

from pkl import Ledger
from pkl.serialization import export_ledger, import_ledger


def make_ledger():
    ledger = Ledger()
    claim = ledger.create_claim("A testable claim", "researcher")
    ledger.add_evidence(claim.id, "Evidence", "A controlled observation", source="lab")
    ledger.assess_claim(claim.id, "supported", evidence_level="E2", summary="Evidence recorded")
    return ledger


def test_round_trip_preserves_verified_state():
    ledger = make_ledger()
    restored = import_ledger(export_ledger(ledger))
    assert restored.verify() is True
    assert restored.current_state() == ledger.current_state()
    assert len(restored.events) == len(ledger.events)


def test_tampered_event_payload_is_rejected_on_import():
    raw = json.loads(export_ledger(make_ledger()))
    raw["audit"][0]["payload"]["text"] = "forged"
    with pytest.raises(ValueError, match="integrity"):
        import_ledger(json.dumps(raw))


def test_deleted_audit_event_is_rejected_on_import():
    raw = json.loads(export_ledger(make_ledger()))
    del raw["audit"][1]
    with pytest.raises(ValueError, match="integrity"):
        import_ledger(json.dumps(raw))


def test_reordered_audit_events_are_rejected_on_import():
    raw = json.loads(export_ledger(make_ledger()))
    raw["audit"][0], raw["audit"][1] = raw["audit"][1], raw["audit"][0]
    with pytest.raises(ValueError, match="integrity"):
        import_ledger(json.dumps(raw))


def test_snapshot_version_is_checked():
    raw = json.loads(export_ledger(make_ledger()))
    raw["version"] = 999
    with pytest.raises(ValueError, match="version"):
        import_ledger(json.dumps(raw))
