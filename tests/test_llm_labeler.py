import pytest

from src.llm_labeler import parse_label


def test_parse_label_clean_relevant():
    assert (parse_label("RELEVANT") is True) is True


def test_parse_label_lower_case_relevant():
    assert (parse_label("relevant") is True) is True


def test_parse_label_clean_irrelevant():
    assert (parse_label("NOT_RELEVANT") is False) is True


def test_parse_label_lower_case_not_relevant():
    assert (parse_label("not_relevant") is False) is True


def test_parse_label_empty_sentence_returns_none():
    assert (parse_label("") is None) is True


def test_parse_label_relevant_sentence():
    assert (parse_label("I would say this is relevant") is True) is True
