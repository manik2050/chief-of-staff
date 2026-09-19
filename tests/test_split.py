from chief_of_staff.dataset import split_by_company


def test_split_by_company_keeps_siblings_together():
    rows = [
        {"company_id": "alpha", "n": 1},
        {"company_id": "alpha", "n": 2},
        {"company_id": "beta", "n": 1},
        {"company_id": "gamma", "n": 1},
        {"company_id": "delta", "n": 1},
        {"company_id": "epsilon", "n": 1},
    ]
    result = split_by_company(rows, train_ratio=0.6, validation_ratio=0.2, seed=3)
    alpha_splits = {
        name
        for name in ("train", "validation", "test")
        if any(row["company_id"] == "alpha" for row in result[name])
    }
    assert alpha_splits == {"train"} or len(alpha_splits) == 1
    assert len([row for row in result[list(alpha_splits)[0]] if row["company_id"] == "alpha"]) == 2

    companies = (
        set(result["train_company_ids"])
        | set(result["validation_company_ids"])
        | set(result["test_company_ids"])
    )
    assert companies == {"alpha", "beta", "gamma", "delta", "epsilon"}
    assert not (
        set(result["train_company_ids"]) & set(result["validation_company_ids"])
    )
    assert not (set(result["train_company_ids"]) & set(result["test_company_ids"]))
    assert not (
        set(result["validation_company_ids"]) & set(result["test_company_ids"])
    )
    assert result["train_company_ids"]
    assert result["validation_company_ids"]
    assert result["test_company_ids"]
