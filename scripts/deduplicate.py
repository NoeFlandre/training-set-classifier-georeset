from src.config import SAMPLES_DIR
from src.dedup import find_duplicates, shingles, split_sentence_to_words

sentence = "This is an example of sentence"
sentences = [
    "This is an example of sentence with enough words for this test",
    "This is an example of sentence with enough words for this test",
    "This was an example of sentence with enough words for this test",
    "This is a completely different kind of sentence",
]


def main():
    print("==== Checking whether my word splitting is working === ")
    words = split_sentence_to_words(sentence)
    print(words)

    print("---- Checking whether shingles are working----")
    n_grams = shingles(sentence=sentence, n=3)
    print(n_grams)

    print(
        "=== Checking whether my pipeline can find duplicates and near duplicates ==="
    )
    sentence_dedup = find_duplicates(sentences)
    print(sentence_dedup)

    print("===  Checking the filtered files ===")

    files = sorted(SAMPLES_DIR.glob("*.filtered.txt"))
    if not files:
        print(f"There are not files with the extension .filtered.txt in {SAMPLES_DIR}")
        return
    print(files)

    print("=== Checking sentences in the files  ===")

    for path in files:
        sentences_per_file = [
            line.strip()
            for line in path.read_text(encoding="utf8").splitlines()
            if line.strip()
        ]

        unique_sentences_per_file = find_duplicates(sentences_per_file)

        print(
            f"First two unique sentences for {path} : {unique_sentences_per_file[:2]}"
        )

        print("=== Saving sentences ===")
        output_path = path.with_name(path.stem + ".deduped.txt")
        output_path.write_text("\n".join(unique_sentences_per_file), encoding="utf8")

        print(f"=== {path} ===")
        print(f"Number of total sentences : {len(sentences_per_file)}")
        print(f"Number of unique sentences : {len(unique_sentences_per_file)}")
        print(f"Unique sentences saved to {output_path}")


if __name__ == "__main__":
    main()
