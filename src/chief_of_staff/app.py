from __future__ import annotations

import os
from collections import defaultdict, deque
from pathlib import Path
from time import time

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from chief_of_staff import __version__
from chief_of_staff.evaluate import score_example
from chief_of_staff.generate import (
    AdapterGenerator,
    HeuristicGenerator,
    PromptOnlyGenerator,
    timed_generate,
)
from chief_of_staff.pii import strip_sensitive
from chief_of_staff.prompts import StartupBrief, render_prompt


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="CHIEF_OF_STAFF_", extra="ignore", env_file=".env"
    )
    api_key: str = ""
    generator: str = "heuristic"
    base_model: str = "Qwen/Qwen2.5-1.5B-Instruct"
    adapter_dir: str = "artifacts/adapters/v1"
    rate_limit_per_minute: int = 30


settings = Settings()
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")


class GenerateRequest(BaseModel):
    brief: str = Field(min_length=12)
    industry: str | None = None
    stage: str | None = None
    traction: str | None = None
    fundraising_goal: str | None = None
    evidence: str | None = None
    consent_to_improve: bool = False


class GenerateResponse(BaseModel):
    pitch_copy: str
    generator: str
    model_version: str
    latency_ms: float
    evaluation: dict
    prompt: str


def build_generator():
    mode = settings.generator.lower()
    if mode == "prompt":
        return PromptOnlyGenerator()
    if mode == "adapter":
        return AdapterGenerator(settings.base_model, settings.adapter_dir)
    return HeuristicGenerator()


generator = build_generator()
request_times: dict[str, deque[float]] = defaultdict(deque)
metrics = {
    "requests": 0,
    "errors": 0,
    "empty_outputs": 0,
    "retries": 0,
    "unsupported_claim_reports": 0,
}


def check_rate_limit(client: str) -> None:
    now = time()
    window = request_times[client]
    while window and now - window[0] > 60:
        window.popleft()
    if len(window) >= settings.rate_limit_per_minute:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    window.append(now)


app = FastAPI(title="Chief of Staff", version=__version__)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.middleware("http")
async def auth_and_metrics(request: Request, call_next):
    if request.url.path.startswith("/generate") and settings.api_key:
        provided = request.headers.get("x-api-key", "")
        if provided != settings.api_key:
            return JSONResponse({"detail": "Unauthorized"}, status_code=401)
    try:
        response = await call_next(request)
    except Exception:
        metrics["errors"] += 1
        raise
    return response


@app.get("/health")
def health() -> dict:
    return {
        "ok": True,
        "version": __version__,
        "generator": generator.name,
        "adapter": settings.adapter_dir if generator.name == "adapter" else None,
    }


@app.get("/pipeline")
def pipeline() -> dict:
    root = Path.cwd()
    checks = {
        "source_records": (root / "data/examples/source_records.json").exists(),
        "reviewed_examples": (root / "data/examples/reviewed_examples.jsonl").exists(),
        "split_manifest": (root / "data/splits/v1.json").exists(),
        "train_split": (root / "data/processed/train.jsonl").exists(),
        "adapter": (root / settings.adapter_dir).exists(),
    }
    return {
        "baselines": ["heuristic (v0)", "prompt-only", "prompt + retrieval", "fine-tuned adapter"],
        "active_generator": generator.name,
        "checks": checks,
        "next": (
            "Train QLoRA on a GPU after the prompt-only baseline fails a specific eval."
            if not checks["adapter"]
            else "Adapter present. Compare it against the prompt-only scorecard."
        ),
    }


@app.get("/metrics")
def get_metrics() -> dict:
    return {
        **metrics,
        "generator": generator.name,
        "model_version": settings.generator,
    }


@app.post("/generate", response_model=GenerateResponse)
def generate(payload: GenerateRequest, request: Request) -> GenerateResponse:
    check_rate_limit(request.client.host if request.client else "local")
    metrics["requests"] += 1
    brief = StartupBrief(
        brief=payload.brief,
        industry=payload.industry,
        stage=payload.stage,
        traction=payload.traction,
        fundraising_goal=payload.fundraising_goal,
        evidence=payload.evidence,
    )
    text, latency_ms = timed_generate(generator, brief)
    if not text.strip():
        metrics["empty_outputs"] += 1
    if payload.consent_to_improve:
        stored = strip_sensitive(brief.source_text())
        _ = stored  # Opt-in store is a private follow-up; never auto-collect.
    score = score_example(
        brief.source_text(),
        text,
        latency_ms=latency_ms,
        prompt_chars=len(render_prompt(brief)),
    )
    return GenerateResponse(
        pitch_copy=text,
        generator=generator.name,
        model_version=settings.generator,
        latency_ms=latency_ms,
        evaluation={
            "plain_text_compliant": score.plain_text_compliant,
            "unsupported_numbers": score.unsupported_numbers,
            "numeric_error": score.numeric_error,
            "repetition": score.repetition,
            "empty_output": score.empty_output,
        },
        prompt=render_prompt(brief),
    )


@app.post("/generate.txt", response_class=PlainTextResponse)
def generate_plain(payload: GenerateRequest, request: Request) -> str:
    result = generate(payload, request)
    return result.pitch_copy


@app.post("/feedback")
def feedback(unsupported_claim: bool = False, retry: bool = False) -> dict:
    if unsupported_claim:
        metrics["unsupported_claim_reports"] += 1
    if retry:
        metrics["retries"] += 1
    return {"ok": True}


@app.get("/")
def index() -> FileResponse:
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))
