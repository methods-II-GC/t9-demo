#!/usr/bin/env python

import gzip

import nltk

# You gotta do this once. Annoying. Whatever.
assert nltk.download("punkt_tab")


def main() -> None:
    with gzip.open("news.2008.en.shuffled.deduped.gz", "rt") as source:
        for line in source:
            print(
                " ".join(
                    token.casefold() for token in nltk.word_tokenize(line)
                )
            )


if __name__ == "__main__":
    main()
