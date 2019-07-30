#!/usr/bin/env python3
import os
import argparse
import logging

from . import fsts_to_flair


def main():
    parser = argparse.ArgumentParser("flair_train")
    parser.add_argument(
        "--fst",
        action="append",
        default=[],
        help="Intent FST(s) to include in training data",
    )
    parser.add_argument(
        "--fst-dir",
        help="Directory containing all intent FSTs to include in training data",
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

    fst_paths = [p for p in args.fst]
    if args.fst_dir:
        for f_name in os.listdir(args.fst_dir):
            fst_path = os.path.join(args.fst_dir, f_name)
            if os.path.isfile(fst_path):
                fst_paths.append(fst_path)

    logging.debug(fst_paths)

    fsts_to_flair(
        fst_paths,
        args.embedding,
        args.cache_dir,
        args.data_dir,
        samples=args.samples,
        max_epochs=args.max_epochs,
    )


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
