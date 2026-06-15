"""

Sentence level filtering. A sentence is kept if:
    - Its word count is included between [MIN_WORDS, MAX_WORDS]
    - It ends with a proper punctuation mark: . ! ?
    - It does not end with an ellipsis ("...")
    - Symbol to word ratio is below MAX_SYMBOL_RATIO

"""

import re
from collections.abc import Iterable

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


def word_count(sentence: str) -> int:
    return len(WORD_RE.findall(sentence))


def symbol_count(sentence: str) -> int:
    return len(SYMBOL_RE.findall(sentence))


def is_valid_sentence(sentence: str) -> bool:

    sentence = sentence.strip()
    if not sentence:
        return False

    n_words = word_count(sentence)
    if not MIN_WORDS <= n_words <= MAX_WORDS:
        return False

    n_symbol = symbol_count(sentence)
    symbol_ratio = n_symbol / n_words
    if not symbol_ratio <= MAX_SYMBOL_RATIO:
        return False

    if not TERMINAL_PUNCT_RE.search(sentence):
        return False

    if ELLIPSIS_RE.search(sentence):
        return False

    return True


def filter_sentences(sentences: Iterable[str]) -> list[str]:
    return [s for s in sentences if is_valid_sentence(s)]
