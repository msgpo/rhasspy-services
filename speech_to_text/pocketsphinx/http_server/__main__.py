#!/usr/bin/env python3
import logging

logger = logging.getLogger("http_server")

import sys
import http.server
import argparse
import tempfile
import subprocess
from typing import BinaryIO


class Handler(http.server.BaseHTTPRequestHandler):
    def __init__(self, audio_file, events_file, *args, **kwargs):
        self.audio_file = audio_file
        self.events_file = events_file
        self.chunk_size = 1024
        http.server.BaseHTTPRequestHandler.__init__(self, *args, **kwargs)

    def do_POST(self):
        content_length = int(self.headers["Content-Length"])
        content_type = self.headers.get("Content-Type", "").lower()
        body = self.rfile.read(content_length)
        logging.debug(f"Received {len(body)} byte(s) of type {content_type}")

        # Start listening
        print("start-listening {}", file=self.events_file)
        self.events_file.flush()

        # Write audio data to temp file
        with tempfile.NamedTemporaryFile(mode="wb") as raw_file:
            if content_type == "audio/wav":
                # Assume WAV file; convert with sox
                raw_file.write(wav_to_raw(body))
            else:
                # Assume raw 16-bit 16Khz mono PCM audio
                raw_file.write(body)

            raw_file.seek(0)

            # Write file name
            print(raw_file.name, file=self.audio_file)
            self.audio_file.flush()

            # Done listening
            print("stop-listening {}", file=self.events_file)
            self.events_file.flush()

            # Wait for response
            event, response = sys.stdin.readline().strip().split(" ", maxsplit=1)

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(response.encode())


# -----------------------------------------------------------------------------


def wav_to_raw(wav_data: bytes) -> bytes:
    """Converts WAV data to 16-bit, 16Khz mono with sox."""
    return subprocess.run(
        [
            "sox",
            "-t",
            "wav",
            "-",
            "-r",
            "16000",
            "-e",
            "signed-integer",
            "-b",
            "16",
            "-c",
            "1",
            "-t",
            "raw",
            "-",
        ],
        check=True,
        input=wav_data,
        stdout=subprocess.PIPE,
    ).stdout


# -----------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--audio-file", required=True, help="Path to write audio file names"
    )
    parser.add_argument("--events-file", required=True, help="Path to write events")
    parser.add_argument(
        "--host", help="Host for HTTP server (default=0.0.0.0)", default="0.0.0.0"
    )
    parser.add_argument(
        "--port", type=int, help="Port for HTTP server (default=5000)", default=5000
    )
    parser.add_argument(
        "--debug", action="store_true", help="Print DEBUG messages to console"
    )

    args, rest = parser.parse_known_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    logger.debug(args)
    audio_file = open(args.audio_file, "w")
    events_file = open(args.events_file, "w")

    def make_server(*args, **kwargs):
        return Handler(audio_file, events_file, *args, **kwargs)

    try:
        logging.debug(f"Starting web server at http://{args.host}:{args.port}")
        http.server.HTTPServer((args.host, args.port), make_server).serve_forever()
    except KeyboardInterrupt:
        pass


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
