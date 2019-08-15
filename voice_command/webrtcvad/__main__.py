#!/usr/bin/env python3
import logging

logger = logging.getLogger("webrtcvad_rhasspy")

import os
import sys
import argparse

from voice_command.webrtcvad.webrtcvad_rhasspy import wait_for_command

# -------------------------------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser("webrtcvad")
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
        help="Seconds of speech before voice command is considered started (default=0.5)",
        type=float,
        default=0.5,
    )
    parser.add_argument(
        "--silence-seconds",
        help="Seconds of silence before voice command is considered stopped (default=0.5)",
        type=float,
        default=0.5,
    )
    parser.add_argument(
        "--debug", action="store_true", help="Print DEBUG messages to standard out"
    )

    args, _ = parser.parse_known_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    logging.debug(args)

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

    wait_for_command(
        audio_file=audio_file,
        events_in_file=events_in_file,
        events_out_file=events_out_file,
        vad_mode=args.vad_mode,
        chunk_size=args.chunk_size,
        min_seconds=args.min_seconds,
        max_seconds=args.max_seconds,
        speech_seconds=args.speech_seconds,
        silence_seconds=args.silence_seconds,
    )


# -------------------------------------------------------------------------------------------------


if __name__ == "__main__":
    main()
