from __future__ import annotations

import os
import time
from typing import Protocol

from chief_of_staff import SYSTEM_PROMPT
from chief_of_staff.clean import clean_text
from chief_of_staff.prompts import StartupBrief, render_prompt, user_content


class Generator(Protocol):
    name: str

    def generate(self, brief: StartupBrief) -> str: ...


class HeuristicGenerator:
    """v0 baseline: restate only what the brief already contains."""

    name = "heuristic"

    def generate(self, brief: StartupBrief) -> str:
        product = clean_text(brief.brief)
        paragraphs = [product]
        if brief.industry or brief.traction:
            bits = []
            if brief.industry:
                bits.append(f"The work is focused on {clean_text(brief.industry)}.")
            if brief.traction:
                bits.append(clean_text(brief.traction))
            paragraphs.append(" ".join(bits))
        closing = []
        if brief.stage:
            closing.append(f"The company is at {clean_text(brief.stage)} stage.")
        if brief.fundraising_goal:
            goal = clean_text(brief.fundraising_goal).rstrip(".")
            if goal and goal[0].isupper() and not goal.isupper():
                goal = goal[0].lower() + goal[1:]
            closing.append(f"The fundraising goal is to {goal}.")
        if closing:
            paragraphs.append(" ".join(closing))
        return "\n\n".join(paragraphs)


class PromptOnlyGenerator:
    """Baseline 1: same system prompt, no adapter, OpenAI-compatible API."""

    name = "prompt"

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
    ) -> None:
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self.base_url = (base_url or os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")).rstrip("/")
        self.model = model or os.environ.get("OPENAI_MODEL", "gpt-4.1-mini")

    def generate(self, brief: StartupBrief) -> str:
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is required for the prompt-only generator")
        import httpx

        payload = {
            "model": self.model,
            "temperature": 0.2,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content(brief)},
            ],
        }
        response = httpx.post(
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json=payload,
            timeout=60,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()


class AdapterGenerator:
    """Baseline 3: Qwen + LoRA adapter served in-process."""

    name = "adapter"

    def __init__(self, base_model: str, adapter_dir: str) -> None:
        self.base_model = base_model
        self.adapter_dir = adapter_dir
        self._pipe = None

    def _load(self):
        if self._pipe is not None:
            return self._pipe
        from peft import PeftModel
        from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

        tokenizer = AutoTokenizer.from_pretrained(self.adapter_dir)
        model = AutoModelForCausalLM.from_pretrained(self.base_model, device_map="auto")
        model = PeftModel.from_pretrained(model, self.adapter_dir)
        self._pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)
        return self._pipe

    def generate(self, brief: StartupBrief) -> str:
        pipe = self._load()
        prompt = render_prompt(brief)
        result = pipe(prompt, max_new_tokens=320, do_sample=False)[0]["generated_text"]
        if result.startswith(prompt):
            result = result[len(prompt) :]
        return result.strip()


def timed_generate(generator: Generator, brief: StartupBrief) -> tuple[str, float]:
    started = time.perf_counter()
    text = generator.generate(brief)
    latency_ms = round((time.perf_counter() - started) * 1000, 1)
    return text, latency_ms
