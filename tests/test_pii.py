from chief_of_staff.pii import strip_sensitive


def test_strip_sensitive_removes_contact_details():
    text = "Call founder Jane Smith at 415-555-0100 or jane@example.com"
    cleaned = strip_sensitive(text)
    assert "jane@example.com" not in cleaned
    assert "415-555-0100" not in cleaned
    assert "[email removed]" in cleaned
    assert "[phone removed]" in cleaned
