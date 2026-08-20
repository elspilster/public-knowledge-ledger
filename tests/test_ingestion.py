from pkl import Ledger
from pkl.ingestion import ingest_source, source_sha256


def test_ingestion_preserves_source_identity_and_integrity_metadata():
    ledger = Ledger()
    claim = ledger.create_claim("A source-backed claim")
    content = "The source says the claim is supported."

    evidence = ingest_source(
        ledger,
        claim.id,
        content=content,
        excerpt="The source says the claim is supported.",
        retrieved_at="2026-08-20T00:00:00+00:00",
        source_type="document",
        extraction_method="manual_excerpt",
        extraction_version="1",
        uri="https://example.invalid/source",
        title="Example source",
        publisher="Example publisher",
        supports_claim=True,
    )

    record = evidence.metadata["source_record"]
    assert evidence.source == "https://example.invalid/source"
    assert record["content_sha256"] == source_sha256(content)
    assert record["extraction_method"] == "manual_excerpt"
    assert record["excerpt"] == evidence.description
    assert ledger.replay_state()["evidence"][evidence.id]["metadata"]["source_record"] == record


def test_ingestion_does_not_invent_missing_source_metadata():
    ledger = Ledger()
    claim = ledger.create_claim("A claim with incomplete source metadata")

    evidence = ingest_source(
        ledger,
        claim.id,
        content="Known content",
        excerpt="Known content",
        retrieved_at="2026-08-20T00:00:00+00:00",
        source_type="unknown_document",
        extraction_method="manual_excerpt",
    )

    record = evidence.metadata["source_record"]
    assert record["uri"] is None
    assert record["title"] is None
    assert record["publisher"] is None
    assert record["publication_date"] is None


def test_changed_source_content_changes_integrity_identifier():
    assert source_sha256("Version one") != source_sha256("Version two")
