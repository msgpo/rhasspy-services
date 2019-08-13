#!/usr/bin/env python3
import logging

logger = logging.getLogger("kaldi_rhasspy")

import os
import sys
import argparse
import json
import threading
import subprocess
import wave
import io
import tempfile
from typing import Optional, Dict, Any, Set

import jsonlines

# -------------------------------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser("kaldi")
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
    parser.add_argument("--model-dir", required=True, help="Directory with kaldi model")
    parser.add_argument(
        "--model-type", required=True, choices=["nnet3", "gmm"], help="Kaldi model type"
    )
    parser.add_argument("--graph-dir", help="Path to directory with HCLG.fst")
    parser.add_argument(
        "--kaldi-dir", required=True, help="Path to kaldi top-level directory"
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

    # Start listening for events
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

                    result = transcribe(
                        audio_data,
                        args.kaldi_dir,
                        args.model_dir,
                        args.model_type,
                        args.graph_dir,
                    )
                    logging.debug(result)

                    with jsonlines.Writer(sys.stdout) as out:
                        out.write(result)
                    sys.stdout.flush()
    else:
        # Read all data from audio file, decode, and stop
        audio_data = audio_file.read()
        result = transcribe(
            audio_data, args.kaldi_dir, args.model_dir, args.model_type, args.graph_dir
        )
        with jsonlines.Writer(sys.stdout) as out:
            out.write(result)


# -------------------------------------------------------------------------------------------------


def transcribe(
    audio_bytes: bytes,
    kaldi_dir: str,
    model_dir: str,
    model_type: str,
    graph_dir: Optional[str] = None,
):
    with tempfile.NamedTemporaryFile(suffix=".wav", mode="wb") as temp_file:
        wav_bytes = buffer_to_wav(audio_bytes)
        temp_file.write(wav_bytes)
        temp_file.seek(0)

        kaldi_cmd = [
            "kaldi-decode",
            "--kaldi-dir",
            kaldi_dir,
            "--model-dir",
            model_dir,
            "--model-type",
            model_type,
        ]

        if graph_dir:
            kaldi_cmd.extend(["--graph-dir", graph_dir])

        # Execute kaldi decode
        logging.debug(kaldi_cmd)

        try:
            result = json.loads(
                subprocess.run(
                    kaldi_cmd,
                    input=f"{temp_file.name}\n".encode(),
                    check=True,
                    stdout=subprocess.PIPE,
                ).stdout
            )
        except Exception as e:
            logger.exception("transcribe")

            # Empty result
            result = {
                "text": "",
                "wav_name": "",
                "wav_seconds": 0,
                "transcribe_seconds": 0,
            }

        return result


# -------------------------------------------------------------------------------------------------


def buffer_to_wav(buffer: bytes) -> bytes:
    """Wraps a buffer of raw audio data (16-bit, 16Khz mono) in a WAV"""
    with io.BytesIO() as wav_buffer:
        with wave.open(wav_buffer, mode="wb") as wav_file:
            wav_file.setframerate(16000)
            wav_file.setsampwidth(2)
            wav_file.setnchannels(1)
            wav_file.writeframesraw(buffer)

        return wav_buffer.getvalue()


# -------------------------------------------------------------------------------------------------


if __name__ == "__main__":
    main()
