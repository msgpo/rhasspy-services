#!/usr/bin/env python3
import logging

logger = logging.getLogger("porcupine_rhasspy")

import os
import sys
import argparse

from wake_word.porcupine.porcupine_rhasspy import wait_for_wake_word

# -------------------------------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser("porcupine")
    parser.add_argument(
        "--audio-file",
        help="File to raw audio data from (16-bit 16Khz mono PCM)",
        default=None,
    )
    parser.add_argument(
        "--events-in-file",
        help="File to read events from (one per line, topic followed by JSON)",
        default=None,
    )
    parser.add_argument(
        "--events-out-file",
        help="File to write events to (one per line, topic followed by JSON)",
        default=None,
    )
    parser.add_argument(
        "--library", required=True, help="Path to porcupine shared library (.so)"
    )
    parser.add_argument(
        "--model", required=True, help="Path to porcupine model parameters (.pv)"
    )
    parser.add_argument(
        "--keyword",
        required=True,
        action="append",
        help="Path to porcupine keyword file(s) (.ppn)",
        default=[],
    )
    parser.add_argument(
        "--sensitivity",
        help="Sensitivity of keyword(s) (0-1)",
        type=float,
        action="append",
        default=[],
    )
    parser.add_argument(
        "--auto-start", action="store_true", help="Start listening immediately"
    )
    parser.add_argument(
        "--debug", action="store_true", help="Print DEBUG messages to console"
    )

    args, _ = parser.parse_known_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    logger.debug(args)

    # -------------------------------------------------------------------------

    if args.audio_file:
        audio_file = open(audio_file, "r")
    else:
        audio_file = sys.stdin.buffer

    # File to read events from
    events_in_file = None
    if args.events_in_file and (args.events_in_file != "-"):
        events_in_file = open(args.events_in_file, "r")

    # File to write events to
    events_out_file = sys.stdout
    if args.events_out_file and (args.events_out_file != "-"):
        events_out_file = open(args.events_out_file, "w")

    # -------------------------------------------------------------------------

    wait_for_wake_word(
        audio_file=audio_file,
        events_in_file=events_in_file,
        events_out_file=events_out_file,
        library=args.library,
        model=args.model,
        keyword=args.keyword,
        sensitivity=args.sensitivity,
        auto_start=args.auto_start,
    )


# -------------------------------------------------------------------------------------------------


if __name__ == "__main__":
    main()
