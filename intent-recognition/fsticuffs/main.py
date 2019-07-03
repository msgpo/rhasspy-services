#!/usr/bin/env python3
import logging

logger = logging.getLogger(__name__)

import os
import sys
import jsonlines
import argparse
import re
from typing import Optional, Dict, Any, Set

import pywrapfst as fst
from jsgf2fst import fstaccept

# -------------------------------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser()
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
        "--debug", action="store_true", help="Print DEBUG messages to console"
    )

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    logging.debug(args)

    # Load intent fst
    intent_fst = fst.Fst.read(args.intent_fst)
    logging.debug(f"Loaded FST from {args.intent_fst}")

    # Add symbols from FST
    known_tokens: Optional[Set[str]] = None

    if args.skip_unknown:
        known_tokens = set()
        in_symbols = intent_fst.input_symbols()
        for i in range(in_symbols.num_symbols()):
            token = in_symbols.find(i).decode()
            known_tokens.add(token)

        logging.debug(f"Skipping words outside of set: {known_tokens}")

    # Recognize lines from stdin
    for line in sys.stdin:
        line = line.strip()
        if len(line) == 0:
            continue

        logging.debug(line)

        if args.lower:
            line = line.lower()

        intent = recognize(intent_fst, line, known_tokens)

        # Output to stdout
        with jsonlines.Writer(sys.stdout) as out:
            out.write(intent)

        sys.stdout.flush()

# -------------------------------------------------------------------------------------------------


def recognize(
    intent_fst: fst.Fst, text: str, known_tokens: Optional[Set[str]] = None
) -> Dict[str, Any]:
    tokens = re.split("\s+", text)

    if known_tokens:
        # Filter tokens
        tokens = [t for t in tokens if t in known_tokens]

    # Only run acceptor if there are any tokens
    if len(tokens) > 0:
        intents = fstaccept(intent_fst, tokens)
    else:
        intents = []

    logging.debug(f"Recognized {len(intents)} intent(s)")

    # Use first intent
    if len(intents) > 0:
        intent = intents[0]

        # Add slots
        intent["slots"] = {}
        for ev in intent["entities"]:
            intent["slots"][ev["entity"]] = ev["value"]

        # Add alternative intents
        intent["intents"] = []
        for other_intent in intents[1:]:
            intent["intents"].append(other_intent)
    else:
        intent = empty_intent()

    return intent


# -------------------------------------------------------------------------------------------------


def empty_intent() -> Dict[str, Any]:
    return {
        "text": "",
        "intent": {"name": "", "confidence": 0},
        "entities": [],
        "intents": [],
        "slots": {},
    }


# -------------------------------------------------------------------------------------------------


if __name__ == "__main__":
    main()
