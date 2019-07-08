#!/usr/bin/env python3
import logging

logger = logging.getLogger(__name__)

import os
import sys
import jsonlines
import time
import argparse
import threading
import struct

from porcupine import Porcupine

# -------------------------------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser()
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
        "--auto-start", action="store_true", help="Start listening immediately"
    )
    parser.add_argument(
        "--debug", action="store_true", help="Print DEBUG messages to console"
    )

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    logging.debug(args)

    audio_file = sys.stdin.buffer
    if args.audio_file:
        audio_file = open(args.audio_file, "rb")

    # Ensure each keyword has a sensitivity value
    sensitivities = args.sensitivity
    while len(sensitivities) < len(args.keyword):
        sensitivities.append(0.5)

    # Load porcupine
    handle = Porcupine(
        args.library,
        args.model,
        keyword_file_paths=args.keyword,
        sensitivities=sensitivities,
    )

    chunk_size = handle.frame_length * 2
    chunk_format = "h" * handle.frame_length

    logging.debug(
        f"Loaded porcupine (keywords={args.keyword}, sensitivities={sensitivities})"
    )

    logging.debug(
        f"Expecting sample rate={handle.sample_rate}, frame length={handle.frame_length}"
    )

    if args.events_file or args.auto_start:
        listening = False

        # Read thread
        def read_audio():
            nonlocal listening, handle
            try:
                while True:
                    chunk = audio_file.read(chunk_size)
                    if len(chunk) > 0:
                        if listening:
                            # Process audio chunk
                            chunk = struct.unpack_from(chunk_format, chunk)
                            keyword_index = handle.process(chunk)

                            if keyword_index:
                                if len(args.keyword) == 1:
                                    keyword_index = 0

                                logging.debug(f"Keyword {keyword_index} detected")
                                result = {
                                    "index": keyword_index,
                                    "keyword": args.keyword[keyword_index],
                                }

                                with jsonlines.Writer(sys.stdout) as out:
                                    out.write(result)

                                sys.stdout.flush()
                    else:
                        time.sleep(0.01)
            except Exception as e:
                logging.exception("read_audio")

        threading.Thread(target=read_audio, daemon=True).start()

        if args.auto_start:
            logging.debug("Automatically started listening")
            listening = True

        if args.events_file:
            # Wait for start/stop events
            with open(args.events_file, "r") as events:
                while True:
                    line = events.readline().strip()
                    if len(line) == 0:
                        continue

                    logging.debug(line)
                    topic, event = line.split(" ", maxsplit=1)
                    if topic == args.event_start:
                        # Clear buffer and start reading
                        listening = True
                        logging.debug("Started listening")
                    elif topic == args.event_stop:
                        # Stop reading and transcribe
                        listening = False
                        logging.debug("Stopped listening")

        else:
            # Wait forever
            threading.Event().wait()

    else:
        # Read all data from audio file, process, and stop
        audio_data = audio_file.read()
        while len(audio_data) > 0:
            chunk = audio_data[:chunk_size]
            audio_data = audio_data[chunk_size:]

            if len(chunk) == chunk_size:
                # Process audio chunk
                chunk = struct.unpack_from(chunk_format, chunk)
                keyword_index = handle.process(chunk)

                if keyword_index:
                    if len(args.keyword) == 1:
                        keyword_index = 0

                    logging.debug(f"Keyword {keyword_index} detected")
                    result = {
                        "index": keyword_index,
                        "keyword": args.keyword[keyword_index],
                    }

                    with jsonlines.Writer(sys.stdout) as out:
                        out.write(result)


# -------------------------------------------------------------------------------------------------


if __name__ == "__main__":
    main()
