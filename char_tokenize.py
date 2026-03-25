#!/usr/bin/env python
"""Despite the name this really just removes punctuation and numbers."""

import gzip
import re


def main() -> None:
    with gzip.open("news.2008.en.shuffled.deduped.gz", "rt") as source:
        for line in source:
            line = line.rstrip().casefold()
            line = re.sub(r"[^a-z ]", "", line)
            line = re.sub(r"\s+", " ", line)
            print(line)


if __name__ == "__main__":
    main()
