from chief_of_staff.evaluate import looks_like_structured_output, score_example, summarize_scores


def test_structured_output_is_not_plain_text():
    assert looks_like_structured_output('{"title": "Problem", "bullets": []}')
    assert looks_like_structured_output("Slide 1: Team")
    assert not looks_like_structured_output("Independent clinics lose revenue every week.")


def test_score_example_flags_invented_metrics():
    score = score_example(
        "We help clinics send reminders.",
        "We grew 300% to $40M ARR.",
    )
    assert score.numeric_error
    assert "300%" in score.unsupported_numbers
    assert "$40M" in score.unsupported_numbers
    assert score.plain_text_compliant


def test_summarize_scores():
    scores = [
        score_example("a", "a grounded paragraph"),
        score_example("a", '{"title": "x"}'),
    ]
    summary = summarize_scores(scores)
    assert summary["examples"] == 2
    assert summary["plain_text_compliance"] == 0.5
