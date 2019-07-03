#!/usr/bin/env python3
import os
import re
import sys
import argparse
import tempfile
import logging
import time

logging.basicConfig(level=logging.DEBUG)

from jsgf import parser as jsgf_parser
from jsgf2fst import jsgf2fst, read_slots, make_intent_fst, fst2arpa

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--grammar-dir", required=True, help="Input directory with JSGF grammars"
    )
    parser.add_argument(
        "--fst", required=True, help="Path to write intent finite state transducer"
    )
    parser.add_argument(
        "--arpa", required=True, help="Path to write ARPA language model"
    )
    parser.add_argument(
        "--vocab", help="Path to write vocabulary"
    )
    parser.add_argument(
        "--fst-dir", help="Output directory for finite state transducers", default=None
    )
    parser.add_argument(
        "--slots-dir", help="Directory with slot value files", default=None
    )
    args = parser.parse_args()

    if not args.fst_dir:
        args.fst_dir = tempfile.TemporaryDirectory().name

    # Create output directory
    os.makedirs(args.fst_dir, exist_ok=True)

    # Ready slots values
    if args.slots_dir:
        logging.debug(f"Loading slot values from {args.slots_dir}")

        # $colors -> [red, green, blue, ...]
        slots = read_slots(slots_dir)
    else:
        slots = {}

    # Load all grammars
    grammars = []
    for f_name in os.listdir(args.grammar_dir):
        logging.debug(f"Parsing JSGF grammar {f_name}")
        grammar = jsgf_parser.parse_grammar_file(os.path.join(args.grammar_dir, f_name))
        grammars.append(grammar)

    # Generate FSTs
    start_time = time.time()
    grammar_fsts = jsgf2fst(grammars, slots=slots)
    for grammar_name, grammar_fst in grammar_fsts.items():
        fst_path = os.path.join(args.fst_dir, grammar_name) + ".fst"
        grammar_fst.write(fst_path)

    # Join into master intent FST
    intent_fst = make_intent_fst(grammar_fsts)
    intent_fst.write(args.fst)
    logging.debug(f"Wrote intent FST to {args.fst}")

    fst_time = time.time() - start_time
    logging.debug(f"Generated FSTs in {fst_time} second(s)")

    # Write ARPA FST
    fst2arpa(args.fst, args.arpa)
    logging.debug(f"Wrote ARPA language model to {args.arpa}")

    if args.vocab:
        # Write vocabulary
        in_symbols = intent_fst.input_symbols()
        with open(args.vocab, "w") as vocab_file:
            for i in range(in_symbols.num_symbols()):
                word = in_symbols.find(i).decode()
                if not word.startswith("__") and not word.startswith("<"):
                    print(word, file=vocab_file)

        logging.debug(f"Wrote vocabulary to {args.vocab}")

# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
