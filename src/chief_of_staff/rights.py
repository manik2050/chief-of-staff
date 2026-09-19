from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

RightsStatus = Literal["approved", "synthetic_original", "rejected", "pending"]


class SourceRecord(BaseModel):
    source_id: str
    source_url: str = ""
    owner: str
    rights_status: RightsStatus
    permission_scope: str
    commercial_use_permitted: bool
    redistribution_permitted: bool
    rights_reviewed_at: date
    private_evidence_ref: str = ""
    notes: str = ""


class DownloadManifestEntry(BaseModel):
    url: str
    filename: str
    sha256: str
    bytes: int
    downloaded_at: str
    skipped: bool = False
    skip_reason: str = ""


class PageRecord(BaseModel):
    document_sha256: str
    page_number: int
    native_characters: int
    machine_draft_text: str = ""
    machine_draft_engine: str
    machine_draft_status: str
    machine_draft_latency_ms: float
    review_status: str = "machine_draft_unverified"
    gold_text: str = ""
    numbers: list[str] = Field(default_factory=list)
