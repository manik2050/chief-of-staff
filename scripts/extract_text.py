#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from chief_of_staff.config import load_toml
from chief_of_staff.extract import extract_pdf


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract native PDF text. Keep empty pages.")
    parser.add_argument("--config", default="configs/data.toml")
    args = parser.parse_args()
    config = load_toml(args.config)
    raw_dir = Path(config["raw_dir"])
    ocr_dir = Path(config["ocr_dir"])
    if not raw_dir.exists():
        print(f"{raw_dir} is empty. Add permission-cleared PDFs first.")
        return
    for pdf in sorted(raw_dir.glob("*.pdf")):
        records = extract_pdf(
            pdf,
            ocr_dir,
            min_native_chars=int(config.get("native_text_min_chars", 40)),
        )
        empty = sum(1 for row in records if row["machine_draft_status"] == "empty")
        print(f"{pdf.name}: {len(records)} pages, {empty} empty (kept)")


if __name__ == "__main__":
    main()
