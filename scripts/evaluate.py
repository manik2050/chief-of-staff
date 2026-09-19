#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from chief_of_staff.dataset import read_jsonl, write_json
from chief_of_staff.evaluate import score_example, summarize_scores
from chief_of_staff.generate import HeuristicGenerator, PromptOnlyGenerator, timed_generate
from chief_of_staff.prompts import StartupBrief, user_content


def brief_from_messages(row: dict) -> StartupBrief:
    user = next(m["content"] for m in row["messages"] if m["role"] == "user")
    fields = {"brief": "", "industry": None, "stage": None, "traction": None, "fundraising_goal": None, "evidence": None}
    current = None
    brief_lines: list[str] = []
    buckets: dict[str, list[str]] = {k: [] for k in fields if k != "brief"}
    mapping = {
        "startup brief": "brief",
        "industry": "industry",
        "stage": "stage",
        "traction": "traction",
        "fundraising goal": "fundraising_goal",
        "evidence": "evidence",
    }
    for line in user.splitlines():
        key = line.strip().lower().rstrip(":")
        if key in mapping:
            current = mapping[key]
            continue
        if current == "brief" or current is None:
            brief_lines.append(line)
            current = "brief"
        elif current:
            buckets[current].append(line)
    fields["brief"] = "\n".join(brief_lines).strip()
    for key, lines in buckets.items():
        text = "\n".join(lines).strip()
        fields[key] = text or None
    return StartupBrief(**fields)


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate a generator against held-out companies.")
    parser.add_argument("--split", default="data/processed/test.jsonl")
    parser.add_argument("--generator", choices=["heuristic", "prompt"], default="heuristic")
    parser.add_argument("--output", default="artifacts/eval/scorecard.json")
    args = parser.parse_args()

    if args.generator == "prompt":
        generator = PromptOnlyGenerator()
    else:
        generator = HeuristicGenerator()

    rows = read_jsonl(Path(args.split))
    scores = []
    samples = []
    for row in rows:
        brief = brief_from_messages(row)
        text, latency_ms = timed_generate(generator, brief)
        score = score_example(
            brief.source_text(),
            text,
            latency_ms=latency_ms,
            prompt_chars=len(user_content(brief)),
        )
        scores.append(score)
        samples.append(
            {
                "company_id": row.get("company_id"),
                "output": text,
                "unsupported_numbers": score.unsupported_numbers,
            }
        )
    summary = summarize_scores(scores)
    summary["generator"] = generator.name
    summary["samples"] = samples
    write_json(Path(args.output), summary)
    print(json.dumps({k: v for k, v in summary.items() if k not in {"scores", "samples"}}, indent=2))


if __name__ == "__main__":
    main()
