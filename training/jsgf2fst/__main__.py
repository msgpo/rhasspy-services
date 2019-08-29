#!/usr/bin/env python3
import logging

logger = logging.getLogger("jsgf2fst")

import argparse

from .jsgf2fst import make_intent_fst


def main():
    parser = argparse.ArgumentParser("jsgf2fst")
    parser.add_argument(
        "--grammar-dir", required=True, help="Input directory with JSGF grammars"
    )
    parser.add_argument(
        "--fst", required=True, help="Path to write intent finite state transducer"
    )
    parser.add_argument(
        "--arpa", required=True, help="Path to write ARPA language model"
    )
    parser.add_argument("--vocab", help="Path to write vocabulary")
    parser.add_argument(
        "--fst-dir", help="Output directory for finite state transducers"
    )
    parser.add_argument("--slots-dir", help="Directory with slot value files")
    parser.add_argument("--whitelist", help="File with grammar names to process")
    parser.add_argument(
        "--debug", action="store_true", help="Print DEBUG messages to the console"
    )
    args, _ = parser.parse_known_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    whitelist = None
    if args.whitelist:
        with open(args.whitelist, "r") as whitelist_file:
            whitelist = set([line.strip() for line in whitelist_file])

    make_fst(
        args.grammar_dir,
        args.fst,
        arpa_path=args.arpa,
        vocab_path=args.vocab,
        fst_dir=args.fst_dir,
        slots_dir=args.slots_dir,
        grammar_whitelist=whitelist,
    )


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
