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
        "--events-file",
        help="File to read events from (one per line, topic followed by JSON)",
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
        "--event-start",
        help="Topic to start reading audio data (default=start)",
        default="start",
    )
    parser.add_argument(
        "--event-stop",
        help="Topic to stop reading audio data (default=stop)",
        default="stop",
    )
    parser.add_argument(
        "--event-detected",
        help="Topic to publish when wake word is detected (default=detected)",
        default="detected",
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

    logging.debug(args)

    wait_for_wake_word(**vars(args))


# -------------------------------------------------------------------------------------------------


if __name__ == "__main__":
    main()
