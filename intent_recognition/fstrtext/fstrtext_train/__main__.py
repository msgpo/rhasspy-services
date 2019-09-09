#!/usr/bin/env python3
import argparse

import pywrapfst as fst

from training.jsgf2fst import make_slot_acceptor


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--intent-fst", required=True, help="Path to intent finite state transducer"
    )
    parser.add_argument("--slot-fst", required=True, help="Path to write slot acceptor")

    args, _ = parser.parse_known_args()

    intent_fst = fst.Fst.read(args.intent_fst)
    slot_fst = make_slot_acceptor(intent_fst)
    slot_fst.write(args.slot_fst)


# -----------------------------------------------------------------------------


if __name__ == "__main__":
    main()
