#!/usr/bin/env python3
import logging

logger = logging.getLogger("pocketsphinx_rhasspy")

import os
import sys
import argparse
import json
import threading
import time
from collections import defaultdict
from typing import Optional, Dict, Any, Set

import jsonlines
import pocketsphinx

from speech_to_text.pocketsphinx.pocketsphinx_rhasspy import get_decoder, transcribe

# -------------------------------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser("pocketsphinx")
    parser.add_argument(
        "--audio-file",
        help="File to raw audio data from (16-bit 16Khz mono PCM)",
        default=None,
    )
    parser.add_argument(
        "--audio-file-lines",
        action="store_true",
        help="Audio file contains one file name per line instead of audio data",
    )
    parser.add_argument(
        "--chunk-size",
        help="Number of bytes to read from audio file at a time",
        type=int,
        default=1024,
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
        "--nbest",
        type=int,
        default=0,
        help="Include up to N best alternative transcriptions",
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
        "--event-reload",
        help="Topic to reload decoder (default=reload)",
        default="stop",
    )
    parser.add_argument(
        "--event-captured",
        help="Topic to report transcription (default=captured)",
        default="captured",
    )
    parser.add_argument(
        "--debug", action="store_true", help="Print DEBUG messages to console"
    )

    args, _ = parser.parse_known_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    logger.debug(args)

    audio_file = sys.stdin.buffer
    if args.audio_file and not (args.audio_file == "-"):
        if not args.audio_file_lines:
            # Contains raw audio data
            audio_file = open(args.audio_file, "rb")
        else:
            # Contains file paths to raw audio files
            audio_file = open(args.audio_file, "r")

    # Load pocketsphinx decoder
    decoder = get_decoder(
        args.acoustic_model,
        args.dictionary,
        args.language_model,
        mllr_matrix=args.mllr_matrix,
        debug=args.debug,
    )

    # File to read events from
    events_in_file = None
    if args.events_in_file:
        if args.events_in_file == "-":
            events_in_file = sys.stdin
        else:
            events_in_file = open(args.events_in_file, "r")

    # File to write events to
    events_out_file = sys.stdout
    if args.events_out_file and not (args.events_out_file == "-"):
        events_out_file = open(args.events_out_file, "w")

    # -------------------------------------------------------------------------

    if events_in_file:
        # Audio buffers keyed by request id
        audio_data: Dict[str, bytes] = {}

        # Lock for audio_data
        audio_data_lock = threading.Lock()

        # Read thread (asynchronous)
        if not args.audio_file_lines:

            def read_audio():
                nonlocal audio_data, audio_data_lock
                try:
                    while True:
                        chunk = audio_file.read(args.chunk_size)
                        if len(chunk) > 0:
                            with audio_data_lock:
                                # Add to all active buffers
                                for key in audio_data:
                                    audio_data[key] += chunk
                        else:
                            # Avoid 100% CPU usage
                            time.sleep(0.01)
                except Exception as e:
                    logger.exception("read_audio")

            threading.Thread(target=read_audio, daemon=True).start()

        # Wait for start/stop events
        for line in events_in_file:
            line = line.strip()
            if len(line) == 0:
                continue

            logger.debug(line)

            # Expected <topic> <payload> on each line
            topic, event = line.split(" ", maxsplit=1)
            if topic.startswith(args.event_start):
                # Everything after expected topic is request id
                request_id = topic[len(args.event_start) :]

                if args.audio_file_lines:
                    # Get next file path
                    audio_path = audio_file.readline().strip()
                    logging.debug(f"Reading {audio_path}")
                    with open(audio_path, "rb") as actual_audio_file:
                        # Read entire file
                        audio_data[request_id] = actual_audio_file.read()
                else:
                    # Clear buffer and start reading asynchronously
                    with audio_data_lock:
                        audio_data[request_id] = bytes()

                    logger.debug(f"Started listening (request_id={request_id})")

            elif topic.startswith(args.event_stop):
                # Everything after expected topic is response id
                response_id = topic[len(args.event_stop) :]

                # Stop reading and transcribe
                with audio_data_lock:
                    audio_buffer = audio_data.pop(response_id, bytes())
                    logger.debug(
                        f"Stopped listening. Decoding {len(audio_buffer)} bytes (response_id={response_id})"
                    )

                result = transcribe(decoder, audio_buffer, nbest=args.nbest)
                logger.debug(result.get("text", ""))

                # Merge stop event data into result
                try:
                    event_dict = json.loads(event)
                    for key, value in event_dict.items():
                        result[key] = value
                except:
                    pass

                # Write output event
                print(args.event_captured + response_id, end=" ", file=events_out_file)

                with jsonlines.Writer(events_out_file) as out:
                    out.write(result)

                events_out_file.flush()
            elif topic.startswith(args.event_reload):
                # Re-load pocketsphinx decoder
                logger.debug("Reloading decoder.")

                try:
                    # Load new settings
                    event_dict = json.loads(event)
                    args.acoustic_model = event_dict.get(
                        "acoustic-model", args.acoustic_model
                    )
                    args.language_model = event_dict.get(
                        "language-model", args.language_model
                    )
                    args.dictionary = event_dict.get("dictionary", args.dictionary)
                    args.mllr_matrix = event_dict.get("mllr-matrix", args.mllr_matrix)
                except Exception as e:
                    logger.exception("reload")

                # Load decoder again
                decoder = get_decoder(
                    args.acoustic_model,
                    args.dictionary,
                    args.language_model,
                    mllr_matrix=args.mllr_matrix,
                    debug=args.debug,
                )

    else:
        # Read all data from audio file, decode, and stop
        audio_buffer = audio_file.read()
        result = transcribe(decoder, audio_buffer)
        with jsonlines.Writer(sys.stdout) as out:
            out.write(result)


# -------------------------------------------------------------------------------------------------


if __name__ == "__main__":
    main()
