from __future__ import annotations

import hashlib
import json
import random
from collections import defaultdict
from pathlib import Path


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def company_id_from_example(row: dict) -> str:
    if row.get("company_id"):
        return str(row["company_id"])
    raise ValueError("Every training example must include company_id")


def split_by_company(
    rows: list[dict],
    *,
    train_ratio: float = 0.8,
    validation_ratio: float = 0.1,
    seed: int = 17,
) -> dict[str, list[dict]]:
    """Split by company, never by page or example index."""
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[company_id_from_example(row)].append(row)

    company_ids = sorted(grouped)
    rng = random.Random(seed)
    rng.shuffle(company_ids)

    n = len(company_ids)
    if n < 3:
        raise ValueError("Need at least 3 companies to create train/validation/test splits")

    n_train = max(1, round(n * train_ratio))
    n_val = max(1, round(n * validation_ratio))
    if n_train + n_val >= n:
        n_train = max(1, n - 2)
        n_val = 1

    train_ids = company_ids[:n_train]
    val_ids = company_ids[n_train : n_train + n_val]
    test_ids = company_ids[n_train + n_val :]
    if not test_ids:
        test_ids = [val_ids.pop()] if len(val_ids) > 1 else [train_ids.pop()]

    def collect(ids: list[str]) -> list[dict]:
        items: list[dict] = []
        for company_id in ids:
            items.extend(grouped[company_id])
        return items

    return {
        "train": collect(train_ids),
        "validation": collect(val_ids),
        "test": collect(test_ids),
        "train_company_ids": sorted(train_ids),
        "validation_company_ids": sorted(val_ids),
        "test_company_ids": sorted(test_ids),
    }
