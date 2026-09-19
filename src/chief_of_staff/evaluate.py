from __future__ import annotations

import re
from dataclasses import asdict, dataclass

from chief_of_staff.numbers import unsupported_numbers

SLIDE_MARKERS = (
    "slide 1",
    "slide 2",
    '"title":',
    '"bullets":',
    "{",
)
JSON_HINT = re.compile(r"^\s*[\{\[]", re.MULTILINE)
REPEATED_LINE = re.compile(r"(.{12,})\n(?:\1\n?){2,}")


@dataclass
class ExampleScore:
    plain_text_compliant: bool
    unsupported_numbers: list[str]
    numeric_error: bool
    empty_output: bool
    repetition: bool
    latency_ms: float
    prompt_chars: int
    output_chars: int
    output_tokens_est: int


def looks_like_structured_output(text: str) -> bool:
    lowered = text.lower()
    if any(marker in lowered for marker in SLIDE_MARKERS):
        return True
    if JSON_HINT.search(text) and ("title" in lowered or "bullets" in lowered):
        return True
    return False


def has_repetition(text: str) -> bool:
    if REPEATED_LINE.search(text):
        return True
    words = text.split()
    if len(words) < 12:
        return False
    unique = len(set(words))
    return unique / len(words) < 0.35


def score_example(
    source: str,
    generated: str,
    *,
    latency_ms: float = 0.0,
    prompt_chars: int = 0,
) -> ExampleScore:
    generated = generated.strip()
    invented = sorted(unsupported_numbers(source, generated))
    return ExampleScore(
        plain_text_compliant=not looks_like_structured_output(generated),
        unsupported_numbers=invented,
        numeric_error=bool(invented),
        empty_output=not generated,
        repetition=has_repetition(generated),
        latency_ms=latency_ms,
        prompt_chars=prompt_chars,
        output_chars=len(generated),
        output_tokens_est=max(1, len(generated.split())) if generated else 0,
    )


def summarize_scores(scores: list[ExampleScore]) -> dict:
    n = len(scores) or 1
    numeric_errors = sum(item.numeric_error for item in scores)
    unsupported = sum(item.numeric_error for item in scores)
    return {
        "examples": len(scores),
        "plain_text_compliance": round(
            sum(item.plain_text_compliant for item in scores) / n, 4
        ),
        "unsupported_claim_rate": round(unsupported / n, 4),
        "numeric_error_rate": round(numeric_errors / n, 4),
        "empty_output_rate": round(sum(item.empty_output for item in scores) / n, 4),
        "repetition_rate": round(sum(item.repetition for item in scores) / n, 4),
        "avg_latency_ms": round(sum(item.latency_ms for item in scores) / n, 1),
        "avg_output_chars": round(sum(item.output_chars for item in scores) / n, 1),
        "scores": [asdict(item) for item in scores],
    }
