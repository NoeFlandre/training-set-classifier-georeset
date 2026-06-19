from src.dedup import shingles


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
