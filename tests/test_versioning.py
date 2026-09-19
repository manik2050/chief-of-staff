from chief_of_staff.versioning import VersionRecord


def test_version_record_requires_rollback_fields():
    record = VersionRecord(
        version="v1",
        base_model="Qwen/Qwen2.5-1.5B-Instruct",
        dataset_hash="abc",
        num_train_examples=200,
        rollback_artifact="artifacts/adapters/v0",
        known_failure_modes=["long briefs > 500 tokens"],
    )
    dumped = record.model_dump()
    assert dumped["rollback_artifact"].endswith("v0")
    assert dumped["num_train_examples"] == 200
