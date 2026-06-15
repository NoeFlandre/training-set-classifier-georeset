from pathlib import Path

from src.config import SAMPLES_DIR
from src.sentence_filtering import filter_sentences, split_sentences


def main():
    files = sorted(SAMPLES_DIR.glob("*.txt"))
    if not files:
        print(f"There are no files in {SAMPLES_DIR}")

    for path in files:
        text = path.read_text(encoding="utf8")
        sentences = split_sentences(text)
        filtered_sentences = filter_sentences(sentences)
        output_path = path.with_name(path.stem + ".filtered.txt")
        output_path.write_text("\n".join(filtered_sentences), encoding="utf8")
        print(f"========== {path}=============")
        print(filtered_sentences)
        print(f"Saved {len(filtered_sentences)} sentences to {output_path}")


if __name__ == "__main__":
    main()
