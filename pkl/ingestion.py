"""Bounded source-to-evidence ingestion for PKL M4.

The module deliberately does not fetch URLs. It records source material supplied
by the caller, derives a deterministic integrity hash, and preserves extraction
context as evidence metadata.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Any

from .ledger import Ledger
from .models import Evidence, EvidenceProfile


@dataclass(frozen=True)
class SourceRecord:
    uri: str | None
    title: str | None
    publisher: str | None
    publication_date: str | None
    retrieved_at: str
    source_type: str
    content_sha256: str
    extraction_method: str
    extraction_version: str
    excerpt: str
    metadata: dict[str, Any]


def source_sha256(content: str) -> str:
    return sha256(content.encode("utf-8")).hexdigest()


def ingest_source(
    ledger: Ledger,
    claim_id: str,
    *,
    content: str,
    excerpt: str,
    retrieved_at: str,
    source_type: str,
    extraction_method: str,
    extraction_version: str = "1",
    uri: str | None = None,
    title: str | None = None,
    publisher: str | None = None,
    publication_date: str | None = None,
    contributor_id: str | None = None,
    supports_claim: bool | None = None,
    profile: EvidenceProfile | None = None,
    metadata: dict[str, Any] | None = None,
) -> Evidence:
    """Record supplied source material without fetching or inventing metadata."""
    if not content:
        raise ValueError("Source content is required")
    if not excerpt:
        raise ValueError("Evidence excerpt is required")
    if not retrieved_at:
        raise ValueError("retrieved_at is required")
    if not source_type:
        raise ValueError("source_type is required")
    if not extraction_method:
        raise ValueError("extraction_method is required")
    if not extraction_version:
        raise ValueError("extraction_version is required")

    record = SourceRecord(
        uri=uri,
        title=title,
        publisher=publisher,
        publication_date=publication_date,
        retrieved_at=retrieved_at,
        source_type=source_type,
        content_sha256=source_sha256(content),
        extraction_method=extraction_method,
        extraction_version=extraction_version,
        excerpt=excerpt,
        metadata=dict(metadata or {}),
    )
    source_metadata = dict(record.metadata)
    source_metadata["source_record"] = {
        "uri": record.uri,
        "title": record.title,
        "publisher": record.publisher,
        "publication_date": record.publication_date,
        "retrieved_at": record.retrieved_at,
        "source_type": record.source_type,
        "content_sha256": record.content_sha256,
        "extraction_method": record.extraction_method,
        "extraction_version": record.extraction_version,
        "excerpt": record.excerpt,
    }
    return ledger.add_evidence(
        claim_id,
        title=record.title or "Untitled source excerpt",
        description=record.excerpt,
        source=record.uri,
        contributor_id=contributor_id,
        supports_claim=supports_claim,
        profile=profile,
        metadata=source_metadata,
    )
