from __future__ import annotations

import re

NUMBER_PATTERN = re.compile(
    r"(?<!\w)(?:[$€£₹]?\s*)?\d[\d,.]*(?:\.\d+)?(?:\s*[%xXMBKmk])?"
)


def numeric_strings(text: str) -> set[str]:
    found: set[str] = set()
    for match in NUMBER_PATTERN.findall(text):
        token = match.replace(" ", "")
        if token.endswith(".") and not re.search(r"\.\d", token):
            token = token[:-1]
        if token:
            found.add(token)
    return found


def unsupported_numbers(source: str, generated: str) -> set[str]:
    """Numbers in output that do not appear in the source evidence."""
    return numeric_strings(generated) - numeric_strings(source)
