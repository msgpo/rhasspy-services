#!/usr/bin/env python3
import logging

logger = logging.getLogger("pocketsphinx_rhasspy")

import os
import sys
import argparse
import json
import threading
from typing import Optional, Dict, Any, Set

import jsonlines
import pocketsphinx

from pocketsphinx_rhasspy import get_decoder, transcribe

# -------------------------------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--audio-file",
        help="File to raw audio data from (16-bit 16Khz mono PCM)",
        default=None,
    )
    parser.add_argument(
        "--chunk-size",
        help="Number of bytes to read from audio file at a time (0 = synchronous read)",
        type=int,
        default=1024,
    )
    parser.add_argument(
        "--events-file",
        help="File to read events from (one per line, topic followed by JSON)",
        default=None,
    )
    parser.add_argument(
        "--acoustic-model", required=True, help="Directory with Sphinx acoustic model"
    )
    parser.add_argument(
        "--dictionary", required=True, help="Path to CMU phonetic dictionary"
    )
    parser.add_argument(
        "--language-model", required=True, help="Path to ARPA language model"
    )
    parser.add_argument(
        "--mllr-matrix", help="Path to tuned acoustic model MLLR matrix", default=None
    )
    parser.add_argument(
        "--event-start",
        help="Topic to start reading audio data (default=start)",
        default="start",
    )
    parser.add_argument(
        "--event-stop",
        help="Topic to stop reading audio data and transcribe (default=stop)",
        default="stop",
    )
    parser.add_argument(
        "--debug", action="store_true", help="Print DEBUG messages to console"
    )

    args, _ = parser.parse_known_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    logger.debug(args)

    # True if audio should be read entirely from a file each time
    audio_sync = args.chunk_size <= 0
    if audio_sync and not args.audio_file:
        logger.fatal("Audio file required if audio sync is on (chunk_size = 0)")
        sys.exit(1)

    audio_file = sys.stdin.buffer
    if args.audio_file and not audio_sync:
        audio_file = open(args.audio_file, "rb")

    # Load pocketsphinx decoder
    decoder = get_decoder(
        args.acoustic_model,
        args.dictionary,
        args.language_model,
        mllr_matrix=args.mllr_matrix,
        debug=args.debug,
    )

    if args.events_file:
        listening = False
        audio_data = bytes()

        # Read thread (asynchronous)
        if not audio_sync:

            def read_audio():
                nonlocal listening, audio_data
                try:
                    while True:
                        chunk = audio_file.read(args.chunk_size)
                        if len(chunk) > 0:
                            if listening:
                                audio_data += chunk
                        else:
                            time.sleep(0.01)
                except Exception as e:
                    logger.exception("read_audio")

            threading.Thread(target=read_audio, daemon=True).start()

        # Wait for start/stop events
        with open(args.events_file, "r") as events:
            while True:
                line = events.readline().strip()
                if len(line) == 0:
                    continue

                logger.debug(line)
                topic, event = line.split(" ", maxsplit=1)
                if topic == args.event_start:
                    if audio_sync:
                        with open(args.audio_file, "rb") as audio_file:
                            # Read entire file
                            audio_data = audio_file.read()
                    else:
                        # Clear buffer and start reading asynchronously
                        audio_data = bytes()
                        listening = True
                        logger.debug("Started listening")

                elif topic == args.event_stop:
                    # Stop reading and transcribe
                    listening = False
                    logger.debug(f"Stopped listening. Decoding {len(audio_data)} bytes")
                    result = transcribe(decoder, audio_data)
                    logger.debug(result)
                    with jsonlines.Writer(sys.stdout) as out:
                        out.write(result)

                    sys.stdout.flush()
    else:
        # Read all data from audio file, decode, and stop
        audio_data = audio_file.read()
        result = transcribe(decoder, audio_data)
        with jsonlines.Writer(sys.stdout) as out:
            out.write(result)


# -------------------------------------------------------------------------------------------------


if __name__ == "__main__":
    main()
