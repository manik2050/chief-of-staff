from __future__ import annotations

import re
import unicodedata


def clean_text(text: str) -> str:
    """Remove extraction noise. Do not 'improve' wording or fix numbers."""
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("\x00", "")
    text = text.replace("\u00a0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
