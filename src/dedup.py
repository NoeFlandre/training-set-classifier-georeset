from datasketch import MinHash

from src.sentence_filtering import WORD_RE

DEFAULT_NUM_PERM = 128


def split_sentence_to_words(sentence: str) -> list[str]:
    sentence = sentence.lower()
    return WORD_RE.findall(sentence)


def shingles(sentence: str, n: int = 3) -> set[str]:
    """
    Given a sentence, it returns the set of n-grams, lowercase of this sentence
    """
    words = split_sentence_to_words(sentence)
    sentence_length = len(words)
    if sentence_length < n:
        return set()
    set_of_n_grams = set()

    for i in range(sentence_length - n + 1):
        n_gram = " ".join(words[i : i + n])
        set_of_n_grams.add(n_gram)
    return set_of_n_grams


def make_minhash(
    shingle_set: set[str],
    num_perm: int = DEFAULT_NUM_PERM,
) -> MinHash:
    """

    Build a MinHash signature to approximate Jaccard similarity

    """

    m = MinHash(num_perm=num_perm)
    for shingle in shingle_set:
        m.update(shingle.encode("utf-8"))

    return m
