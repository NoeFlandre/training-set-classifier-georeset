from src.config import SAMPLES_DIR
from src.dedup import find_duplicates


def main():
    files = sorted(SAMPLES_DIR.glob("*.filtered.txt"))
    if not files:
        print(f"There are no .filtered.txt files in {SAMPLES_DIR}")
        return

    for path in files:
        sentences_per_file = [
            line.strip()
            for line in path.read_text(encoding="utf8").splitlines()
            if line.strip()
        ]
        unique_sentences_per_file = find_duplicates(sentences_per_file)
        output_path = path.with_name(path.stem + ".deduped.txt")
        output_path.write_text("\n".join(unique_sentences_per_file), encoding="utf8")
        print(
            f"{path}: {len(sentences_per_file)} sentences -> "
            f"{len(unique_sentences_per_file)} unique, saved to {output_path}"
        )


if __name__ == "__main__":
    main()
