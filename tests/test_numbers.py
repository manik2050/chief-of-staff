from chief_of_staff.numbers import numeric_strings, unsupported_numbers


def test_numeric_strings_finds_money_and_percents():
    text = "Raised $12.5M with 80% retention in 2024."
    found = numeric_strings(text)
    assert "$12.5M" in found
    assert "80%" in found
    assert "2024" in found


def test_unsupported_numbers_are_hallucinations():
    source = "We help clinics reduce missed appointments."
    generated = "Clinics save $2M and grow 40%."
    assert unsupported_numbers(source, generated) == {"$2M", "40%"}


def test_supported_numbers_are_allowed():
    source = "The company reports $1.2M ARR."
    generated = "The company reports $1.2M ARR and is raising a seed round."
    assert unsupported_numbers(source, generated) == set()
