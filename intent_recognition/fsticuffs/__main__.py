#!/usr/bin/env python3
import logging

logger = logging.getLogger("fsticuffs")

import os
import sys
import argparse
import json
from typing import Optional, Dict, Any, Set

import jsonlines
import pywrapfst as fst

from .fsticuffs import recognize, empty_intent, fst_to_graph, recognize_fuzzy

# -------------------------------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser("fsticuffs")
    parser.add_argument(
        "--intent-fst", help="Path to intent finite state transducer", required=True
    )
    parser.add_argument(
        "--skip-unknown",
        action="store_true",
        help="Skip tokens not present in FST input symbol table",
    )
    parser.add_argument(
        "--lower", action="store_true", help="Automatically lower-case input text"
    )
    parser.add_argument(
        "--fuzzy", action="store_true", help="Use fuzzy search (slower)"
    )
    parser.add_argument(
        "--stop-words",
        help="File with words that can be ignored during fuzzy recognition",
    )
    parser.add_argument(
        "--debug", action="store_true", help="Print DEBUG messages to console"
    )

    args, rest = parser.parse_known_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    logger.debug(args)

    # Load intent fst
    intent_fst = fst.Fst.read(args.intent_fst)
    logger.debug(f"Loaded FST from {args.intent_fst}")

    # Add symbols from FST
    known_tokens: Optional[Set[str]] = None

    if args.skip_unknown:
        # Ignore words outside of input symbol table
        known_tokens = set()
        in_symbols = intent_fst.input_symbols()
        for i in range(in_symbols.num_symbols()):
            token = in_symbols.find(i).decode()
            known_tokens.add(token)

        logger.debug(f"Skipping words outside of set: {known_tokens}")

    intent_graph = None
    stop_words = set()
    if args.fuzzy:
        logger.debug("Fuzzy search enabled")
        intent_graph = fst_to_graph(intent_fst)

        if args.stop_words:
            with open(args.stop_words, "r") as stop_words_file:
                stop_words = set([line.strip() for line in stop_words_file])

    # Recognize lines from stdin
    try:
        for line in sys.stdin:
            line = line.strip()
            if len(line) == 0:
                continue

            logger.debug(line)

            try:
                # Try to interpret as JSON
                request = json.loads(line)
                line = request["text"]
            except:
                pass  # assume line is just text

            if args.lower:
                line = line.lower()

            if args.fuzzy:
                # Fuzzy search
                intent = recognize_fuzzy(
                    intent_graph, line, known_tokens=known_tokens, stop_words=stop_words
                )
            else:
                # Fast (strict) search
                intent = recognize(intent_fst, line, known_tokens)

            # Output to stdout
            with jsonlines.Writer(sys.stdout) as out:
                out.write(intent)

            sys.stdout.flush()
    except KeyboardInterrupt:
        pass


# -------------------------------------------------------------------------------------------------


if __name__ == "__main__":
    main()
