import json
from pathlib import Path

from chief_of_staff.dataset import split_by_company
from chief_of_staff.rights import SourceRecord


def test_reviewed_examples_have_rights_and_company_ids():
    root = Path(__file__).resolve().parents[1]
    records = json.loads((root / "data/examples/source_records.json").read_text())
    assert SourceRecord.model_validate(records[0]).rights_status == "synthetic_original"

    rows = []
    with (root / "data/examples/reviewed_examples.jsonl").open() as handle:
        for line in handle:
            row = json.loads(line)
            assert row["company_id"]
            assert row["review_status"] == "human_reviewed"
            assert row["source_id"] == "synthetic-original"
            rows.append(row)
    assert len({row["company_id"] for row in rows}) >= 3
    result = split_by_company(rows, seed=17)
    clinic = {name for name, items in result.items() if name in {"train", "validation", "test"} and any(r["company_id"] == "clinicflow" for r in items)}
    assert len(clinic) == 1
