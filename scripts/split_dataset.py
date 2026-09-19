#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from chief_of_staff.config import load_toml
from chief_of_staff.dataset import read_jsonl, sha256_file, split_by_company, write_json, write_jsonl


def main() -> None:
    parser = argparse.ArgumentParser(description="Split examples by company, not by page.")
    parser.add_argument("--config", default="configs/data.toml")
    parser.add_argument("--input", default="data/processed/all.jsonl")
    args = parser.parse_args()
    config = load_toml(args.config)
    split_cfg = config.get("split", {})
    rows = read_jsonl(Path(args.input))
    result = split_by_company(
        rows,
        train_ratio=float(split_cfg.get("train_ratio", 0.8)),
        validation_ratio=float(split_cfg.get("validation_ratio", 0.1)),
        seed=int(split_cfg.get("seed", 17)),
    )
    processed = Path(config["processed_dir"])
    for name in ("train", "validation", "test"):
        write_jsonl(processed / f"{name}.jsonl", result[name])

    overlap = (
        set(result["train_company_ids"]) & set(result["validation_company_ids"])
        | set(result["train_company_ids"]) & set(result["test_company_ids"])
        | set(result["validation_company_ids"]) & set(result["test_company_ids"])
    )
    if overlap:
        raise SystemExit(f"Company leak across splits: {overlap}")

    manifest = {
        "split_version": split_cfg.get("version", "v1"),
        "dataset_hash": sha256_file(Path(args.input)),
        "train_company_ids": result["train_company_ids"],
        "validation_company_ids": result["validation_company_ids"],
        "test_company_ids": result["test_company_ids"],
        "counts": {
            "train_examples": len(result["train"]),
            "validation_examples": len(result["validation"]),
            "test_examples": len(result["test"]),
        },
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    write_json(Path(config["split_manifest_path"]), manifest)
    print(json.dumps(manifest["counts"], indent=2))


if __name__ == "__main__":
    main()
