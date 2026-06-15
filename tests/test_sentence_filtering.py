from src.sentence_filtering import (
    MAX_WORDS,
    MIN_WORDS,
    is_valid_sentence,
)


def test_exactly_min_words_kept():
    s = " ".join(["word"] * (MIN_WORDS - 1)) + " end."
    assert is_valid_sentence(s) is True


def test_one_word_below_min_word_rejected():
    s = " ".join(["word"] * (MIN_WORDS - 2)) + " end."
    assert is_valid_sentence(s) is False


def test_exactly_max_words_kept():
    s = " ".join(["word"] * (MAX_WORDS - 1)) + " end."
    assert is_valid_sentence(s) is True


def test_one_word_above_max_words_rejected():
    s = " ".join(["word"] * (MAX_WORDS)) + " end."
    assert is_valid_sentence(s) is False


def test_sentence_with_too_many_symbols_rejected():
    s = " ".join(["@word"] * MIN_WORDS) + " end."
    assert is_valid_sentence(s) is False


def test_sentence_without_terminal_punctuation_rejected():
    s = " ".join(["word"] * MIN_WORDS)
    assert is_valid_sentence(s) is False


def test_sentence_ending_with_ellipsis_rejected():
    s = " ".join(["word"] * MAX_WORDS) + "..."
    assert is_valid_sentence(s) is False


def test_empty_sentence_rejected():
    s = ""
    assert is_valid_sentence(s) is False


def test_white_space_only_rejected():
    s = "   "
    assert is_valid_sentence(s) is False


def test_sentence_ending_with_question_mark_kept():
    s = " ".join(["word"] * MIN_WORDS) + " end?"
    assert is_valid_sentence(s) is True
