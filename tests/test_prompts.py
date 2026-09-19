from chief_of_staff.prompts import StartupBrief, render_prompt, to_chat_example, user_content
from chief_of_staff.prompts import TrainingExample


def test_render_prompt_is_plain_text_instructions():
    brief = StartupBrief(
        brief="We help independent clinics reduce missed appointments.",
        industry="Healthcare",
        stage="Seed",
    )
    prompt = render_prompt(brief)
    assert "Do not return JSON" in prompt
    assert "Healthcare" in prompt
    assert "Seed" in prompt


def test_chat_example_shape():
    example = TrainingExample(
        company_id="clinicflow",
        source_id="synthetic-original",
        brief=StartupBrief(brief="We help clinics."),
        target_copy="Clinics need reminders.",
    )
    chat = to_chat_example(example)
    roles = [m["role"] for m in chat["messages"]]
    assert roles == ["system", "user", "assistant"]
    assert "We help clinics." in user_content(example.brief)
