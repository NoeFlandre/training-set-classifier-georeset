import json
from pathlib import Path

from src.config import SAMPLES_DIR
from src.llm_labeler import make_labeler


def label_file(labeler, input_path: Path) -> dict[str, int]:

    sentences = [
        line.strip()
        for line in input_path.read_text(encoding="utf8").splitlines()
        if line.strip()
    ]

    output_path = input_path.with_name(input_path.stem + ".labeled.jsonl")
    counts = {"relevant": 0, "not_relevant": 0, "unparsed": 0, "errors": 0}

    with output_path.open("w", encoding="utf8") as out:
        for sentence in sentences:
            try:
                label, raw = labeler.label(sentence)

            except Exception as e:
                counts["errors"] += 1
                out.write(
                    json.dumps(
                        {
                            "sentence": sentence,
                            "model": labeler.model_path,
                            "label": None,
                            "raw": None,
                            "error": str(e),
                        }
                    )
                    + "\n"
                )
                continue

            if label is True:
                counts["relevant"] += 1

            elif label is False:
                counts["not_relevant"] += 1

            else:
                counts["unparsed"] += 1

            out.write(
                json.dumps(
                    {
                        "sentence": sentence,
                        "model": labeler.model_path,
                        "label": label,
                        "raw": raw,
                    }
                )
                + "\n"
            )
    return counts


def main():
    labeler = make_labeler()
    files = sorted(SAMPLES_DIR.glob("*.deduped.txt"))

    if not files:
        print(f"There are no files in {SAMPLES_DIR}")
        return

    for path in files:
        counts = label_file(labeler, path)
        print(f"Pathname: {path}")
        print(f"Number of relevant sentences: {counts['relevant']}")
        print(f"Number of irrelevant sentences: {counts['not_relevant']}")
        print(f"Number of unparsed sentences: {counts['unparsed']}")
        print(f"Number of errors: {counts['errors']}")


if __name__ == "__main__":
    main()
