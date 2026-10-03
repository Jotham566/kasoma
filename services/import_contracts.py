"""Structured synthetic content only; no executable or binary upload formats."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import Field, model_validator

from services.content import digest
from services.content_contracts import CreateDraft, DraftDocument, Reason
from services.identity_contracts import Contract


class ImportRecord(Contract):
    subject_id: UUID
    document: DraftDocument
    change_reason: Reason

    def draft(self) -> CreateDraft:
        return CreateDraft(**self.model_dump())


class ImportInput(Contract):
    format_version: Literal["kasoma-draft-import-v1"]
    synthetic: Literal[True]
    records: list[ImportRecord] = Field(min_length=1, max_length=20)

    @model_validator(mode="after")
    def safe_candidates(self) -> "ImportInput":
        hashes = set()
        for row in self.records:
            doc = row.document
            if doc.rights_status != "ORIGINAL_KASOMA" or not all(
                value.strip() for value in [doc.source, doc.source_locator, doc.rights_evidence]
            ):
                raise ValueError("Synthetic provenance and source locator required")
            # Text is never rendered as HTML; reject executable markup on import as well.
            encoded = row.model_dump_json().lower()
            if any(
                marker in encoded
                for marker in ["<script", "<iframe", "<object", "javascript:", "data:text/html"]
            ):
                raise ValueError("Active content is not permitted")
            fingerprint = digest(
                {
                    "subject": str(row.subject_id),
                    "document": doc.model_dump(mode="json", exclude={"source_locator"}),
                }
            )
            if fingerprint in hashes:
                raise ValueError("Duplicate candidate")
            hashes.add(fingerprint)
        if len(self.model_dump_json().encode()) > 65536:
            raise ValueError("Import is too large")
        return self


class ImportResult(Contract):
    position: int
    version_id: UUID
    outcome: Literal["CREATED", "DUPLICATE"]


class ImportView(Contract):
    id: UUID
    status: Literal["QUEUED", "COMPLETED", "FAILED"]
    created_at: datetime
    finished_at: datetime | None
    attempts: int
    error_code: str | None
    results: list[ImportResult]


class ImportPage(Contract):
    data: list[ImportView]
    next_cursor: UUID | None
