#!/usr/bin/env python3
import os
import sys
import argparse
import logging
import subprocess

from ini_jsgf.__main__ import main as ini_jsgf_main
from jsgf_fst_arpa.__main__ import main as jsgf_fst_arpa_main
from vocab_dict.__main__ import main as vocab_dict_main
from vocab_g2p.__main__ import main as vocab_g2p_main

from ini_jsgf import make_grammars
from jsgf_fst_arpa import make_fst
from vocab_dict import make_dict


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--command",
        choices=["ini_jsgf", "jsgf_fst_arpa", "vocab_dict", "vocab_g2p"],
        help="Available commands",
    )
    args, _ = parser.parse_known_args()

    if args.command == "ini_jsgf":
        ini_jsgf_main()
    elif args.command == "jsgf_fst_arpa":
        jsgf_fst_arpa_main()
    elif args.command == "vocab_dict":
        vocab_dict_main()
    elif args.command == "vocab_g2p":
        vocab_g2p_main()
    else:
        make_everything()


# -----------------------------------------------------------------------------


def make_everything():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--ini-file", default=None, help="Path to sentences ini file (default: stdin)"
    )
    parser.add_argument("output_dir", help="Directory to write output files")
    parser.add_argument(
        "--dictionary",
        required=True,
        action="append",
        help="Path to one or more pronunciation dictionaries",
    )
    parser.add_argument(
        "--g2p-model",
        default=None,
        help="Path to grapheme-to-phoneme finite state transducer",
    )
    parser.add_argument(
        "--slots-dir", help="Directory with slot value files", default=None
    )
    args, _ = parser.parse_known_args()

    logging.basicConfig(level=logging.DEBUG)
    logging.debug(args)

    os.makedirs(args.output_dir, exist_ok=True)

    grammar_dir = os.path.join(args.output_dir, "grammars")
    vocab_path = os.path.join(args.output_dir, "vocab.txt")
    unknown_path = os.path.join(args.output_dir, "unknown_words.txt")

    ini_file = sys.stdin
    if args.ini_file:
        ini_file = open(args.ini_file, "r")

    # ini -> jsgf
    make_grammars(ini_file, grammar_dir)

    # jsgf -> fst, arpa
    make_fst(
        grammar_dir,
        os.path.join(args.output_dir, "intent.fst"),
        os.path.join(args.output_dir, "language_model.txt"),
        vocab_path=vocab_path,
        fst_dir=os.path.join(args.output_dir, "fsts"),
    )

    if os.path.exists(unknown_path):
        os.unlink(unknown_path)

    # dictionary
    with open(os.path.join(args.output_dir, "dictionary.txt"), "w") as dictionary_file:
        unknown_words = make_dict(
            vocab_path, args.dictionary, dictionary_file, unknown_path
        )

    guess_path = os.path.join(args.output_dir, "unknown_guess.txt")
    if os.path.exists(guess_path):
        os.unlink(guess_path)

    # unknown words
    if len(unknown_words) > 0:
        assert (
            args.g2p_model is not None
        ), "g2p model is required to guess unknown word pronunciations"
        with open(guess_path, "wb") as guess_file:
            guess_file.write(
                subprocess.check_output(
                    [
                        "phonetisaurus-apply",
                        "--model",
                        args.g2p_model,
                        "--word_list",
                        unknown_path,
                        "--nbest",
                        "1",
                    ]
                )
            )

        logging.warning("There were one or more unknown words.")
        logging.warning(f"See {guess_path} for pronunciation guesses.")
        logging.warning("Add pronunciations to a --dictionary and re-run.")
    else:
        logging.info("Training succeeded")


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
