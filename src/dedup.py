from datasketch import MinHash, MinHashLSH

from src.sentence_filtering import WORD_RE

DEFAULT_NUM_PERM = 128
DEFAULT_THRESHOLD = 0.5
DEFAULT_N = 3


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


def jaccard(a: set[str], b: set[str]) -> float:
    """True Jaccard similarity between two shingle sets"""

    if not a and not b:
        return 1.0

    if not a or not b:
        return 0.0

    return len(a & b) / len(a | b)


def find_duplicates(
    sentences: list[str],
    threshold: float = DEFAULT_THRESHOLD,
    num_perm: int = DEFAULT_NUM_PERM,
    n: int = DEFAULT_N,
) -> list[str]:

    if not 0.0 <= threshold <= 1.0:
        raise ValueError(
            f"Error: threshold should be in the range [0, 1], got {threshold}"
        )

    shingles_sets: list[set[str]] = []
    signatures: list[MinHash | None] = []

    for sentence in sentences:
        s = shingles(sentence, n=n)
        shingles_sets.append(s)
        if not s:
            signatures.append(None)
        else:
            signatures.append(make_minhash(s, num_perm=num_perm))

    lsh = MinHashLSH(threshold=threshold, num_perm=num_perm)
    for i, sig in enumerate(signatures):
        if sig is not None:
            lsh.insert(str(i), sig)

    skip: set[int] = set()
    for i, sentence in enumerate(sentences):
        if i in skip:
            continue

        sig_i = signatures[i]
        if sig_i is None:
            continue

        for cand_key in lsh.query(sig_i):
            j = int(cand_key)
            if j == i or j in skip:
                continue
            if jaccard(shingles_sets[i], shingles_sets[j]) >= threshold:
                skip.add(j)

    return [s for i, s in enumerate(sentences) if i not in skip]
