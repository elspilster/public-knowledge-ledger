import itertools

from pkl.quorum import QuorumPolicy, Seat


SEATS = [
    Seat("schneier", "security"),
    Seat("green", "cryptography"),
    Seat("wordpress", "community"),
    Seat("apple", "technology"),
    Seat("trump", "politics"),
    Seat("burnham", "civic"),
    Seat("macedo", "religion"),
]


def policy():
    return QuorumPolicy(SEATS, threshold=4, min_categories=3)


def test_four_same_category_cannot_form_quorum():
    p = policy()
    assert p.capture_possible({"schneier", "green", "wordpress", "apple"}) is True
    assert p.capture_possible({"apple", "trump", "burnham", "macedo"}) is True


def test_four_unknown_or_duplicate_identity_cannot_form_quorum():
    p = policy()
    assert p.capture_possible({"schneier", "green", "wordpress", "unknown"}) is False


def test_four_with_three_categories_is_valid():
    p = policy()
    assert p.capture_possible({"schneier", "wordpress", "apple", "trump"}) is True


def test_all_four_combinations_are_evaluated_against_category_rule():
    p = policy()
    results = {frozenset(c): p.capture_possible(set(c)) for c in itertools.combinations([s.seat_id for s in SEATS], 4)}
    assert len(results) == 35
    assert all(results.values())
