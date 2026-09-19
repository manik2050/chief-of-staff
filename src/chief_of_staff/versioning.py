from __future__ import annotations

from datetime import date
from typing import Any

from pydantic import BaseModel, Field


class VersionRecord(BaseModel):
    version: str
    base_model: str
    base_model_revision: str = ""
    dataset_hash: str
    num_train_examples: int
    gpu_type: str = "none"
    total_gpu_hours: float = 0.0
    eval_useful_copy: float | None = None
    eval_unsupported_claims: float | None = None
    eval_numeric_errors: float | None = None
    deployment_date: date | None = None
    rollback_artifact: str = ""
    known_failure_modes: list[str] = Field(default_factory=list)
    extra: dict[str, Any] = Field(default_factory=dict)
