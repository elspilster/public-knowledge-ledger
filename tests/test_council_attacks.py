import pytest

from pkl.council import RootCouncil
from pkl.quorum import QuorumPolicy, Seat


SEATS = [Seat("a", "science"), Seat("b", "civil"), Seat("c", "industry"), Seat("d", "public")]


def council():
    return RootCouncil(QuorumPolicy(SEATS, threshold=4, min_categories=3))


def test_three_of_four_cannot_capture_council():
    with pytest.raises(ValueError, match="Quorum"):
        council().decide("claim", "accepted", {"a", "b", "c"}, "capture attempt")


def test_four_signers_from_two_categories_cannot_capture():
    seats = [Seat("a", "science"), Seat("b", "science"), Seat("c", "civil"), Seat("d", "civil")]
    with pytest.raises(ValueError, match="Quorum"):
        RootCouncil(QuorumPolicy(seats, threshold=4, min_categories=3)).decide("claim", "accepted", {"a", "b", "c", "d"}, "category capture")


def test_unknown_signer_cannot_satisfy_quorum():
    with pytest.raises(ValueError, match="Quorum"):
        council().decide("claim", "accepted", {"a", "b", "c", "attacker"}, "forged seat")


def test_membership_change_requires_reason_and_preserves_quorum_rules():
    c = council()
    with pytest.raises(ValueError, match="reason"):
        c.update_membership(SEATS, reason=" ")
    with pytest.raises(ValueError, match="unchanged"):
        c.update_membership(SEATS, reason="no-op")
    new_seats = [Seat("a", "science"), Seat("b", "civil"), Seat("c", "industry"), Seat("e", "public")]
    c.update_membership(new_seats, reason="rotate public seat")
    with pytest.raises(ValueError, match="Quorum"):
        c.decide("claim", "accepted", {"a", "b", "c", "d"}, "old seat replay")
    decision = c.decide("claim", "accepted", {"a", "b", "c", "e"}, "rotated council review")
    assert decision.signers == frozenset({"a", "b", "c", "e"})
    assert c.membership_history_records()[-1]["reason"] == "rotate public seat"


def test_conflicting_decisions_are_recorded_not_hidden():
    c = council()
    first = c.decide("claim", "accepted", {"a", "b", "c", "d"}, "evidence supports claim")
    second = c.decide("claim", "rejected", {"a", "b", "c", "d"}, "new counter-evidence")
    assert c.history("claim") == [first, second]
    assert c.latest("claim") == second
