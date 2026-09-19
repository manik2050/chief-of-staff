from __future__ import annotations

import time
from pathlib import Path

from pypdf import PdfReader

from chief_of_staff.clean import clean_text
from chief_of_staff.dataset import sha256_file, write_json
from chief_of_staff.numbers import numeric_strings
from chief_of_staff.rights import PageRecord


def extract_native_text(page) -> str:
    try:
        return page.extract_text() or ""
    except Exception:  # noqa: BLE001 - extraction failures are recorded, not raised
        return ""


def extract_pdf(
    path: Path,
    output_dir: Path,
    *,
    min_native_chars: int = 40,
    ocr_engine: str | None = None,
) -> list[dict]:
    """Native text first. Empty pages are kept, never dropped."""
    document_hash = sha256_file(path)
    reader = PdfReader(str(path))
    records: list[dict] = []
    output_dir.mkdir(parents=True, exist_ok=True)

    for index, page in enumerate(reader.pages, start=1):
        started = time.perf_counter()
        native = clean_text(extract_native_text(page))
        engine = "pypdf"
        status = "drafted" if native else "empty"
        text = native

        if len(native) < min_native_chars and ocr_engine:
            engine = ocr_engine
            status = "needs_ocr"
            # Optional OCR is plugged in by callers. We never invent text here.

        elapsed_ms = round((time.perf_counter() - started) * 1000, 1)
        record = PageRecord(
            document_sha256=document_hash,
            page_number=index,
            native_characters=len(native),
            machine_draft_text=text,
            machine_draft_engine=engine,
            machine_draft_status=status,
            machine_draft_latency_ms=elapsed_ms,
            review_status="machine_draft_unverified",
            gold_text="",
            numbers=sorted(numeric_strings(text)),
        )
        records.append(record.model_dump())

    dest = output_dir / f"{path.stem}.pages.json"
    write_json(dest, records)
    return records
