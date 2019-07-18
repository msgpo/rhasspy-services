#!/usr/bin/env python3
import logging

logger = logging.getLogger("vocab_dict")

import sys
import argparse

from .vocab_dict import make_dict


def main():
    parser = argparse.ArgumentParser("vocab_dict")
    parser.add_argument("--vocab", required=True, help="Path to vocabulary file")
    parser.add_argument(
        "--dictionary",
        required=True,
        type=str,
        action="append",
        help="Path(s) to dictionary file(s)",
    )
    parser.add_argument("--unknown", help="Path to write unknown words", default=None)
    parser.add_argument(
        "--upper", action="store_true", help="Force upper-case on all words"
    )
    parser.add_argument(
        "--lower", action="store_true", help="Force lower-case on all words"
    )
    parser.add_argument(
        "--no-number", action="store_true", help="Don't number duplicate words"
    )
    parser.add_argument(
        "--debug", action="store_true", help="Print DEBUG messages to the console"
    )
    args, _ = parser.parse_known_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    make_dict(
        args.vocab,
        args.dictionary,
        sys.stdout,
        unknown_path=args.unknown,
        upper=args.upper,
        lower=args.lower,
        no_number=args.no_number,
    )


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
