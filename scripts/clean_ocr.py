#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from chief_of_staff.clean import clean_text
from chief_of_staff.config import load_toml
from chief_of_staff.numbers import numeric_strings


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Clean OCR noise. Never auto-correct numbers."
    )
    parser.add_argument("--config", default="configs/data.toml")
    args = parser.parse_args()
    config = load_toml(args.config)
    ocr_dir = Path(config["ocr_dir"])
    if not ocr_dir.exists():
        print(f"{ocr_dir} does not exist yet.")
        return
    for path in sorted(ocr_dir.glob("*.pages.json")):
        records = json.loads(path.read_text(encoding="utf-8"))
        for record in records:
            text = clean_text(record.get("machine_draft_text") or "")
            record["machine_draft_text"] = text
            record["numbers"] = sorted(numeric_strings(text))
        path.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
        print(f"cleaned {path.name}")


if __name__ == "__main__":
    main()
