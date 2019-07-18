#!/usr/bin/env python3
import logging

logger = logging.getLogger("jsgf_fst_arpa")

import argparse

from .jsgf_fst_arpa import make_fst


def main():
    parser = argparse.ArgumentParser("jsgf_fst_arpa")
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
        "--fst-dir", help="Output directory for finite state transducers", default=None
    )
    parser.add_argument(
        "--slots-dir", help="Directory with slot value files", default=None
    )
    parser.add_argument(
        "--debug", action="store_true", help="Print DEBUG messages to the console"
    )
    args, _ = parser.parse_known_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    make_fst(
        args.grammar_dir,
        args.fst,
        arpa_path=args.arpa,
        vocab_path=args.vocab,
        fst_dir=args.fst_dir,
        slots_dir=args.slots_dir,
    )


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
