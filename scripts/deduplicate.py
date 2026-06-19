from src.dedup import shingles, split_sentence_to_words

sentence = "This is an example of sentence"


def main():
    print("==== Checkig whether my word splitting is working === ")
    words = split_sentence_to_words(sentence)
    print(words)

    print("---- Checking whether shingles are working----")
    n_grams = shingles(sentence=sentence, n=3)
    print(n_grams)


if __name__ == "__main__":
    main()
