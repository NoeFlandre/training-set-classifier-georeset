from src.config import SAMPLES_DIR
from src.extractor import extract_text


def preview_text(text: str, char_count: int) -> str:
    return text[:char_count].replace("\n", " ")


def main():
    files = sorted(SAMPLES_DIR.glob("*html"))
    if not files:
        print(f"There is no file at {SAMPLES_DIR}")

    for path in files:
        html = path.read_text(encoding="utf8")
        text = extract_text(html)
        preview = preview_text(text, 100)
        print(f"-----{path}------")
        print(f"Preview: {preview}")


if __name__ == "__main__":
    main()
