"""Bounded source-to-evidence ingestion for PKL M4.

This module deliberately does not fetch URLs. It records a concrete source
supplied by the caller, derives a content integrity hash, and stores the
extraction context alongside the resulting evidence.
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
    """Return the deterministic SHA-256 integrity identifier for source text."""
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
    """Record a bounded source excerpt as evidence without fetching or guessing."""
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

    source = SourceRecord(
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
    evidence_metadata = dict(source.metadata)
    evidence_metadata["source_record"] = {
        "uri": source.uri,
        "title": source.title,
        "publisher": source.publisher,
        "publication_date": source.publication_date,
        "retrieved_at": source.retrieved_at,
        "source_type": source.source_type,
        "content_sha256": source.content_sha256,
        "extraction_method": source.extraction_method,
        "extraction_version": source.extraction_version,
        "excerpt": source.excerpt,
    }
    return ledger.add_evidence(
        claim_id,
        title=source.title or "Untitled source excerpt",
        description=excerpt,
        source=source.uri,
        contributor_id=contributor_id,
        supports_claim=supports_claim,
        profile=profile,
        metadata=evidence_metadata,
    )
