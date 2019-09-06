#!/usr/bin/env python3
import os
import argparse
import logging

import pywrapfst as fst

from . import fsts_to_flair


def main():
    parser = argparse.ArgumentParser("flair_train")
    parser.add_argument(
        "--intent-fst",
        help="Path to finite state transducer with all intents",
    )
    parser.add_argument(
        "--embedding", required=True, action="append", help="Word embedding(s) to use"
    )
    parser.add_argument(
        "--cache-dir", required=True, help="Directory with Flair models"
    )
    parser.add_argument(
        "--data-dir", required=True, help="Directory to write trained models to"
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=None,
        help="Number of random samples to generate from each intent (default: all sentences)",
    )
    parser.add_argument(
        "--max-epochs",
        type=int,
        default=100,
        help="Maximum number of training epochs (default: 100)",
    )
    parser.add_argument(
        "--debug", action="store_true", help="Print DEBUG messages to console"
    )
    args, _ = parser.parse_known_args()

    if args.debug:
        logging.root.setLevel(logging.DEBUG)

    logging.debug(args)

    intent_fst = fst.Fst.read(args.intent_fst)

    fsts_to_flair(
        intent_fst,
        args.embedding,
        args.cache_dir,
        args.data_dir,
        samples=args.samples,
        max_epochs=args.max_epochs,
    )


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
