from chief_of_staff.clean import clean_text


def test_clean_text_strips_noise_not_numbers():
    raw = "Hello\x00  world\u00a0\n\n\n$12.SM\n\n\n"
    cleaned = clean_text(raw)
    assert "\x00" not in cleaned
    assert cleaned == "Hello world\n\n$12.SM"
