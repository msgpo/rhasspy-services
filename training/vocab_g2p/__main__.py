#!/usr/bin/env python3
import sys
import re
import argparse
from collections import defaultdict
import logging

logger = logging.getLogger("vocab_g2p")

import jsonlines


def main():
    parser = argparse.ArgumentParser("vocab_g2p")
    parser.add_argument(
        "--output", default=None, help="Path to write guesses as JSON (default: stdout)"
    )
    parser.add_argument(
        "--debug", action="store_true", help="Print DEBUG messages to console"
    )
    args, _ = parser.parse_known_args()

    # -------------------------------------------------------------------------

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    logger.debug(args)

    output_file = sys.stdout
    if args.output:
        output_file = open(args.output, "w")

    pronunciations = defaultdict(list)
    for line in sys.stdin:
        word, phonemes = re.split(r"\s+", line.strip(), maxsplit=1)
        pronunciations[word].append(phonemes)

    with jsonlines.Writer(output_file) as out:
        out.write(pronunciations)


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
