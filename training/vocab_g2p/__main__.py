#!/usr/bin/env python3
import sys
import re
from collections import defaultdict

import jsonlines

def main():
    pronunciations = defaultdict(list)
    for line in sys.stdin:
        word, phonemes = re.split(r"\s+", line.strip(), maxsplit=1)
        pronunciations[word].append(phonemes)

    with jsonlines.Writer(sys.stdout) as out:
        out.write(pronunciations)

# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
