#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from chief_of_staff.dataset import write_jsonl
from chief_of_staff.prompts import StartupBrief, TrainingExample, to_chat_example


def row_to_example(row: dict) -> dict:
    brief = StartupBrief(
        brief=row["brief"],
        industry=row.get("industry"),
        stage=row.get("stage"),
        traction=row.get("traction"),
        fundraising_goal=row.get("fundraising_goal"),
        evidence=row.get("evidence"),
    )
    example = TrainingExample(
        company_id=row["company_id"],
        source_id=row["source_id"],
        brief=brief,
        target_copy=row["target_copy"],
        review_status=row.get("review_status", "human_reviewed"),
    )
    chat = to_chat_example(example)
    return chat


def main() -> None:
    parser = argparse.ArgumentParser(description="Build chat JSONL from reviewed examples.")
    parser.add_argument("--input", default="data/examples/reviewed_examples.jsonl")
    parser.add_argument("--output", default="data/processed/all.jsonl")
    args = parser.parse_args()
    rows = []
    with Path(args.input).open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if row.get("review_status") not in {None, "human_reviewed"}:
                continue
            rows.append(row_to_example(row))
    write_jsonl(Path(args.output), rows)
    print(f"Wrote {len(rows)} examples to {args.output}")


if __name__ == "__main__":
    main()
