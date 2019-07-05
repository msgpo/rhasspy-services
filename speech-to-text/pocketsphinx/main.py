#!/usr/bin/env python3
import logging

logger = logging.getLogger(__name__)

import os
import sys
import jsonlines
import time
import argparse
import threading
from typing import Optional, Dict, Any

import pocketsphinx

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
        help="Number of bytes to read from audio file at a time",
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
        "--event-start", help="Topic to start reading audio data", default="start"
    )
    parser.add_argument(
        "--event-stop",
        help="Topic to stop reading audio data and transcribe",
        default="stop",
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
        audio_file = open(args.audio_file, "r")

    # Load pocketsphinx decoder
    decoder = get_decoder(args)

    if args.events_file:
        listening = False
        audio_data = bytes()

        # Read thread
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
                logging.exception("read_audio")

        threading.Thread(target=read_audio, daemon=True).start()

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
                    audio_data = bytes()
                    listening = True
                    logging.debug("Started listening")
                elif topic == args.event_stop:
                    # Stop reading and transcribe
                    listening = False
                    logging.debug(
                        f"Stopped listening. Decoding {len(audio_data)} bytes"
                    )
                    result = transcribe(decoder, audio_data)
                    logging.debug(result)
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


def get_decoder(args) -> pocketsphinx.Decoder:
    """Loads the pocketsphinx decoder from command-line arguments."""
    start_time = time.time()
    decoder_config = pocketsphinx.Decoder.default_config()
    decoder_config.set_string("-hmm", args.acoustic_model)
    decoder_config.set_string("-dict", args.dictionary)
    decoder_config.set_string("-lm", args.language_model)

    if not args.debug:
        decoder_config.set_string("-logfn", os.devnull)

    if args.mllr_matrix and os.path.exists(args.mllr_matrix):
        decoder_config.set_string("-mllr", args.mllr_matrix)

    decoder = pocketsphinx.Decoder(decoder_config)
    end_time = time.time()

    logger.info(f"Successfully loaded decoder in {end_time - start_time} second(s)")

    return decoder


# -------------------------------------------------------------------------------------------------


def transcribe(decoder: pocketsphinx.Decoder, audio_data: bytes) -> Dict[str, Any]:
    """Transcribes audio data to speech."""
    # Process data as an entire utterance
    start_time = time.time()
    decoder.start_utt()
    decoder.process_raw(audio_data, False, True)
    decoder.end_utt()
    end_time = time.time()

    logger.debug(f"Decoded WAV in {end_time - start_time} second(s)")

    transcription = ""
    decode_seconds = end_time - start_time
    likelihood = 0.0
    score = 0

    hyp = decoder.hyp()
    if hyp is not None:
        likelihood = decoder.get_logmath().exp(hyp.prob)
        transcription = hyp.hypstr

    result = {
        "text": transcription,
        "seconds": decode_seconds,
        "likelihood": likelihood,
        "nbest": {nb.hypstr: nb.score for nb in decoder.nbest()},
    }

    return result


# -------------------------------------------------------------------------------------------------


if __name__ == "__main__":
    main()
