#!/usr/bin/env python3
import logging

logger = logging.getLogger("ini_jsgf")

import sys
import argparse

from .ini_jsgf import make_grammars


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--grammar-dir", required=True, help="Output directory for JSGF grammars"
    )
    parser.add_argument(
        "--ini-file", default=None, help="Path to ini file (default=stdin)"
    )
    parser.add_argument(
        "--no-overwrite",
        action="store_true",
        help="Don't overwrite existing grammar files",
    )
    parser.add_argument(
        "--debug", action="store_true", help="Print DEBUG messages to the console"
    )
    args, _ = parser.parse_known_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    if args.ini_file:
        # Read from file
        ini_file = open(args.ini_file, "r")
    else:
        ini_file = sys.stdin
        logging.debug("Reading from standard in")

    make_grammars(ini_file, args.grammar_dir, no_overwrite=args.no_overwrite)


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
