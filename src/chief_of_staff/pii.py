from __future__ import annotations

import re

PHONE = re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?){1,2}\d{4}\b")
EMAIL = re.compile(r"\b[\w.+\-]+@[\w\-]+\.[\w.\-]+\b")
# Conservative: keep company facts, strip obvious personal identifiers.
PERSON_HINT = re.compile(
    r"\b(?:contact|founder|ceo|partner)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b"
)


def strip_sensitive(text: str) -> str:
    text = EMAIL.sub("[email removed]", text)
    text = PHONE.sub("[phone removed]", text)
    text = PERSON_HINT.sub("[name removed]", text)
    return text
