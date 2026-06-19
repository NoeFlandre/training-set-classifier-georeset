import pytest

from src.dedup import find_duplicates, make_minhash, shingles


def test_is_case_insensitive():
    sentence_1 = "the cat sat on the mat"
    sentence_2 = "The Cat Sat On The Mat"

    shingles_sentence_1 = shingles(sentence_1, 2)
    shingles_sentence_2 = shingles(sentence_2, 2)

    assert (shingles_sentence_1 == shingles_sentence_2) is True


def test_short_input_returns_empty_set():
    short_sentence = "Hello"
    shingles_short_sentence = shingles(short_sentence)

    assert (shingles_short_sentence == set()) is True


def test_custom_n_produces_the_right_count():
    sentence = "This is an example of sentence"
    shingles_sentence = shingles(sentence, 2)

    assert (len(shingles_sentence) == 5) is True


def test_make_minhash_perfect_duplicates():
    shingle_set_1 = set(["this is", "an example", "of sentence"])
    shingle_set_2 = set(["this is", "an example", "of sentence"])

    m1 = make_minhash(shingle_set_1)
    m2 = make_minhash(shingle_set_2)

    assert (m1.jaccard(m2) >= 0.9) is True


def test_make_minhash_unrelated_sentences():
    shingle_set_1 = set(["we are", "more than", "what they"])
    shingle_set_2 = set(["this is", "an example", "of sentence"])

    m1 = make_minhash(shingle_set_1)
    m2 = make_minhash(shingle_set_2)

    assert (m1.jaccard(m2) < 0.2) is True


def test_make_minhash_near_duplicates_sentences():
    shingle_set_1 = set(["this was", "an example", "of sentence", "with a", "lot of"])
    shingle_set_2 = set(["this is", "an example", "of sentence", "with a", "lot of"])

    m1 = make_minhash(shingle_set_1)
    m2 = make_minhash(shingle_set_2)

    assert (m1.jaccard(m2) >= 0.6) is True


def test_find_duplicates_returns_empty_list_for_empty_input():
    sentences = []
    results = find_duplicates(sentences)

    assert (results == []) is True


def test_find_duplicates_keep_one_sentence_when_identitical():
    sentences = [
        "This is a sentence",
        "This is a sentence",
        "This is a sentence",
    ]

    results = find_duplicates(sentences)

    assert (results == ["This is a sentence"]) is True


def test_find_duplicates_keeps_unique_sentences():
    sentences = ["This is an example of sentence", "There is a bird next door"]

    results = find_duplicates(sentences)

    assert (results == sentences) is True


def test_find_duplicates_first_seen_wins():
    sentences = [
        "This is an example of sentence to test with enough words because I want them to work",
        "This was an example of sentence to test with enough words because I want them to work",
        "This is an another example of sentence to test with enough words because I want them to work",
        "There is a beautiful flower next door",
    ]

    results = find_duplicates(sentences)

    assert (
        results
        == [
            "This is an example of sentence to test with enough words because I want them to work",
            "There is a beautiful flower next door",
        ]
    ) is True


def test_find_duplicates_threshold_out_of_range_raises_error():
    sentences = ["This is an example"]
    with pytest.raises(ValueError):
        find_duplicates(sentences, threshold=1.5)
