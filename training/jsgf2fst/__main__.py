#!/usr/bin/env python3
import logging

logger = logging.getLogger("jsgf2fst")

import sys
import argparse
import json
from pathlib import Path

import networkx as nx
import pywrapfst as fst

from .jsgf2fst import grammar_to_fsts


def main():
    parser = argparse.ArgumentParser("jsgf2fst")
    parser.add_argument(
        "--replace-fst",
        nargs=2,
        action="append",
        default=[],
        help="Name and FST path to replace",
    )
    parser.add_argument(
        "--fsts-dir", help="Output directory for finite state transducers"
    )
    parser.add_argument(
        "--debug", action="store_true", help="Print DEBUG messages to the console"
    )
    args, _ = parser.parse_known_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    logger.debug(args)

    # JSGF grammar from stdin
    grammar = sys.stdin.read()

    # Load FST replacements
    replace_fsts: Dict[str, fst.Fst] = {n: fst.Fst.read(p) for n, p in args.replace_fst}

    # Parse grammar
    logger.debug("Parsing grammar")
    listener = grammar_to_fsts(grammar, replace_fsts=replace_fsts)

    if args.fsts_dir:
        # Output FSTs
        fsts_dir = Path(args.fsts_dir)

        # Write FST for each rule
        for rule_name, rule_fst in listener.fsts.items():
            fst_path = fsts_dir / f"{rule_name}.fst"
            rule_fst.write(str(fst_path))
            logger.debug(f"Wrote {fst_path}")

    json.dump(nx.readwrite.json_graph.node_link_data(listener.graph), sys.stdout)


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
