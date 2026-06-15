from pathlib import Path

from src.sentence_filtering import filter_sentences, split_sentences


def main():
    path = Path("samples/agriculture.txt")
    text = path.read_text(encoding="utf8")
    sentences = split_sentences(text)
    filtered_sentences = filter_sentences(sentences)
    print(filtered_sentences)


if __name__ == "__main__":
    main()
