from pathlib import Path

from pypdf import PdfWriter

from chief_of_staff.extract import extract_pdf


def _blank_pdf(path: Path, pages: int) -> None:
    writer = PdfWriter()
    for _ in range(pages):
        writer.add_blank_page(width=72, height=72)
    with path.open("wb") as handle:
        writer.write(handle)


def test_extract_keeps_empty_pages(tmp_path):
    pdf = tmp_path / "blank.pdf"
    _blank_pdf(pdf, pages=2)
    records = extract_pdf(pdf, tmp_path / "ocr")
    assert len(records) == 2
    assert all(row["machine_draft_status"] == "empty" for row in records)
    assert all(row["gold_text"] == "" for row in records)
    assert (tmp_path / "ocr" / "blank.pages.json").exists()
