"""First end-to-end PKL example.

This is deliberately a demonstration record, not a scientific database.
"""

from pkl import Ledger


ledger = Ledger()

claim = ledger.create_claim(
    "Earth is approximately spherical (more precisely, an oblate spheroid).",
    contributor_id="PKL-HUMAN-0001",
)

evidence = ledger.add_evidence(
    claim.id,
    "Local vertical changes with geographic position",
    "A plumb-bob defines local vertical. On a curved Earth, sufficiently separated "
    "north/south locations have different local vertical directions. This is a "
    "challengeable physical prediction rather than an appeal to authority.",
    source="PKL prototype example",
    contributor_id="PKL-HUMAN-0001",
    supports_claim=True,
)

evidence.profile.independence_level = "I3"
evidence.profile.methodology_quality = 3
evidence.profile.source_quality = 2
evidence.profile.relevance = 4

challenge = ledger.challenge_claim(
    claim.id,
    "A simple plumb-bob argument should be examined carefully because local vertical "
    "is affected by gravity, rotation, elevation, and local mass distribution.",
    challenger_id="PKL-HUMAN-0002",
    counter_evidence_ids=[evidence.id],
)

ledger.assess_claim(
    claim.id,
    "supported",
    evidence_level="E5",
    summary="The claim has convergent independent support; the plumb-bob challenge does not overturn it.",
)

print(claim)
print(evidence)
print(challenge)
print("History:")
for event in ledger.history(claim.id):
    print(event)
