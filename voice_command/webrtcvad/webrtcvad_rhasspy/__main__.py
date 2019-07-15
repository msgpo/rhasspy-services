#!/usr/bin/env python3
import logging

logger = logging.getLogger("webrtcvad_rhasspy")

import os
import sys
import argparse

from webrtcvad_rhasspy import wait_for_command

# -------------------------------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser("webrtcvad")
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
        "--chunk-size",
        help="Number of bytes to process at a time (default=960)",
        type=int,
        default=960,
    )
    parser.add_argument(
        "--vad-mode",
        help="Sensitivity (1-3, 3 is most sensitive, default=1)",
        type=int,
        default=3,
    )
    parser.add_argument(
        "--min-seconds",
        help="Minimum number of seconds a voice command must last (default=2)",
        type=float,
        default=2,
    )
    parser.add_argument(
        "--max-seconds",
        help="Maximum number of seconds a voice command can last before timeout (default=30)",
        type=float,
        default=30,
    )
    parser.add_argument(
        "--speech-seconds",
        help="Seconds of speech before voice command is considered started (default=0.3)",
        type=float,
        default=0.3,
    )
    parser.add_argument(
        "--silence-seconds",
        help="Seconds of silence before voice command is considered stopped (default=0.5)",
        type=float,
        default=0.5,
    )
    parser.add_argument(
        "--event-start",
        help="Topic to start reading audio data (default=start)",
        default="start",
    )
    parser.add_argument(
        "--event-speech",
        help="Topic when speech is detected (default=speech)",
        default="speech",
    )
    parser.add_argument(
        "--event-silence",
        help="Topic when silence is detected (default=silence)",
        default="silence",
    )
    parser.add_argument(
        "--event-command-start",
        help="Topic when voice command starts (default=command-start)",
        default="command-start",
    )
    parser.add_argument(
        "--event-command-stop",
        help="Topic when voice command stops (default=command-stop)",
        default="command-stop",
    )
    parser.add_argument(
        "--event-command-timeout",
        help="Topic when voice command times out (default=command-timeout)",
        default="command-timeout",
    )
    parser.add_argument(
        "--debug", action="store_true", help="Print DEBUG messages to standard out"
    )

    args, _ = parser.parse_known_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    logging.debug(args)

    wait_for_command(**vars(args))


# -------------------------------------------------------------------------------------------------


if __name__ == "__main__":
    main()
