#!/usr/bin/env python3
import logging

logger = logging.getLogger("jsgf_fst_arpa")

import os
import re
import sys
import tempfile
import time
from typing import Optional

from jsgf import parser as jsgf_parser
from jsgf2fst import jsgf2fst, read_slots, make_intent_fst, fst2arpa


def make_fst(
    grammar_dir: str,
    intent_fst_path: str,
    arpa_path: str,
    vocab_path: Optional[str] = None,
    fst_dir: Optional[str] = None,
    slots_dir: Optional[str] = None,
):
    if not fst_dir:
        fst_dir = tempfile.TemporaryDirectory().name

    # Create output directory
    os.makedirs(fst_dir, exist_ok=True)

    # Ready slots values
    if slots_dir:
        logging.debug(f"Loading slot values from {slots_dir}")

        # $colors -> [red, green, blue, ...]
        slots = read_slots(slots_dir)
    else:
        slots = {}

    # Load all grammars
    grammars = []
    for f_name in os.listdir(grammar_dir):
        logging.debug(f"Parsing JSGF grammar {f_name}")
        grammar = jsgf_parser.parse_grammar_file(os.path.join(grammar_dir, f_name))
        grammars.append(grammar)

    # Generate FSTs
    start_time = time.time()
    grammar_fsts = jsgf2fst(grammars, slots=slots)
    for grammar_name, grammar_fst in grammar_fsts.items():
        fst_path = os.path.join(fst_dir, grammar_name) + ".fst"
        grammar_fst.write(fst_path)

    # Join into master intent FST
    intent_fst = make_intent_fst(grammar_fsts)
    intent_fst.write(intent_fst_path)
    logging.debug(f"Wrote intent FST to {intent_fst_path}")

    fst_time = time.time() - start_time
    logging.debug(f"Generated FSTs in {fst_time} second(s)")

    # Write ARPA FST
    fst2arpa(intent_fst_path, arpa_path)
    logging.debug(f"Wrote ARPA language model to {arpa_path}")

    if vocab_path:
        # Write vocabulary
        in_symbols = intent_fst.input_symbols()
        with open(vocab_path, "w") as vocab_file:
            for i in range(in_symbols.num_symbols()):
                word = in_symbols.find(i).decode()
                if not word.startswith("__") and not word.startswith("<"):
                    print(word, file=vocab_file)

        logging.debug(f"Wrote vocabulary to {vocab_path}")


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
