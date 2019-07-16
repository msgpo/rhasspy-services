#!/usr/bin/env python3
import os
import re
import sys
import argparse
import logging
from typing import Iterable, Optional, List, Dict, Callable


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--vocab", required=True, help="Path to vocabulary file")
    parser.add_argument(
        "--dictionary",
        required=True,
        type=str,
        action="append",
        help="Path(s) to dictionary file(s)",
    )
    parser.add_argument(
        "--unknown", help="Path to write unknown words", default=None
    )
    parser.add_argument(
        "--upper", action="store_true", help="Force upper-case on all words"
    )
    parser.add_argument(
        "--lower", action="store_true", help="Force lower-case on all words"
    )
    parser.add_argument(
        "--no-number", action="store_true", help="Don't number duplicate words"
    )
    args = parser.parse_args()

    transform = lambda w: w
    if args.upper:
        transform = lambda w: w.upper()
    elif args.lower:
        transform = lambda w: w.lower()

    # Read dictionaries
    word_dict: Dict[str, List[str]] = {}
    for dict_path in args.dictionary:
        with open(dict_path, "r") as dict_file:
            read_dict(dict_file, word_dict, transform)

    # Resolve vocabulary
    words_needed = set()
    with open(args.vocab, "r") as vocab_file:
        for word in vocab_file:
            word = word.strip()
            if len(word) == 0:
                continue

            word = transform(word)
            words_needed.add(word)

    # Write output dictionary
    unknown_words = []
    for word in sorted(words_needed):
        if not word in word_dict:
            unknown_words.append(word)
            continue

        for i, pronounce in enumerate(word_dict[word]):
            if (i < 1) or args.no_number:
                print(word, pronounce)
            else:
                print("%s(%s)" % (word, i + 1), pronounce)

    # Write unknown words
    if len(unknown_words) and args.unknown:
        with open(args.unknown, "w") as unknown_file:
            for word in unknown_words:
                print(word, file=unknown_file)

# -----------------------------------------------------------------------------


def read_dict(
    dict_file: Iterable[str],
    word_dict: Optional[Dict[str, List[str]]] = None,
    transform: Optional[Callable[[str], str]] = None,
) -> Dict[str, List[str]]:
    """
    Loads a CMU word dictionary, optionally into an existing Python dictionary.
    """
    if word_dict is None:
        word_dict = {}

    for line in dict_file:
        line = line.strip()
        if len(line) == 0:
            continue

        try:
            # Use explicit whitespace (avoid 0xA0)
            word, pronounce = re.split(r"[ \t]+", line, maxsplit=1)

            idx = word.find("(")
            if idx > 0:
                word = word[:idx]

            if transform:
                word = transform(word)

            pronounce = pronounce.strip()
            if word in word_dict:
                word_dict[word].append(pronounce)
            else:
                word_dict[word] = [pronounce]
        except Exception as e:
            logging.warning(f"read_dict: {e}")

    return word_dict


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
