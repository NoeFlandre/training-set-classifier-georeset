"""

Sentence level filtering. A sentence is kept if:
    - Its word count is included between [MIN_WORDS, MAX_WORDS]
    - It ends with a proper punctuation mark: . ! ?
    - It does not end with an ellipsis ("...")
    - Symbol to word ratio is below MAX_SYMBOL_RATIO

"""

import re

MIN_WORDS = 8
MAX_WORDS = 80
MAX_SYMBOL_RATIO = 0.20

WORD_RE = re.compile(r"\w+")
SYMBOL_RE = re.compile(r"[^\w\s]")
ELLIPSIS_RE = re.compile(r"\.\.\.\s*$")
TERMINAL_PUNCT_RE = re.compile(r"[.?!]\s*$")


def split_sentences(text: str) -> list[str]:
    text = text.replace("\n", " ")
    parts = re.split(r"(?<=[.?!])\s+", text)
    return [p.strip() for p in parts if p.strip()]
