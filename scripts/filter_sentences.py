from pathlib import Path

from src.sentence_filtering import split_sentences


def main():
    path = Path("samples/agriculture.txt")
    text = path.read_text(encoding="utf8")
    sentences = split_sentences(text)
    print(sentences)


if __name__ == "__main__":
    main()
