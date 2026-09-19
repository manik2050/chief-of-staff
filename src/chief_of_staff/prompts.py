from __future__ import annotations

from dataclasses import dataclass, field

from chief_of_staff import SYSTEM_PROMPT


@dataclass
class StartupBrief:
    brief: str
    industry: str | None = None
    stage: str | None = None
    traction: str | None = None
    fundraising_goal: str | None = None
    evidence: str | None = None

    def source_text(self) -> str:
        parts = [self.brief]
        for value in (
            self.industry,
            self.stage,
            self.traction,
            self.fundraising_goal,
            self.evidence,
        ):
            if value:
                parts.append(value)
        return "\n".join(parts)


@dataclass
class TrainingExample:
    company_id: str
    source_id: str
    brief: StartupBrief
    target_copy: str
    review_status: str = "human_reviewed"
    extra: dict = field(default_factory=dict)


def optional_context(brief: StartupBrief) -> str:
    blocks = []
    for label, value in [
        ("Industry", brief.industry),
        ("Stage", brief.stage),
        ("Traction", brief.traction),
        ("Fundraising goal", brief.fundraising_goal),
        ("Evidence", brief.evidence),
    ]:
        if value:
            blocks.append(f"{label}:\n{value}")
    return "\n\n".join(blocks)


def user_content(brief: StartupBrief) -> str:
    context = optional_context(brief)
    if context:
        return f"Startup brief:\n{brief.brief}\n\n{context}"
    return f"Startup brief:\n{brief.brief}"


def render_prompt(brief: StartupBrief) -> str:
    return (
        "Write grounded English funding-pitch copy.\n"
        "Return plain text only. Do not return JSON.\n"
        "Do not invent statistics, customers, revenue, or market size.\n\n"
        f"{user_content(brief)}"
    ).strip()


def to_chat_example(example: TrainingExample) -> dict:
    return {
        "company_id": example.company_id,
        "source_id": example.source_id,
        "review_status": example.review_status,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content(example.brief)},
            {"role": "assistant", "content": example.target_copy},
        ],
    }
