#!/usr/bin/env python3
import logging

logger = logging.getLogger("http_server")

import sys
import http.server
import argparse
import time
import math

import jsonlines


class Handler(http.server.BaseHTTPRequestHandler):
    def __init__(self, audio_file, events_file, *args, **kwargs):
        self.audio_file = audio_file
        self.events_file = events_file
        self.chunk_size = 1024
        http.server.BaseHTTPRequestHandler.__init__(self, *args, **kwargs)

    def do_POST(self):
        content_length = int(self.headers["Content-Length"])
        body = self.rfile.read(content_length)
        logging.debug(f"Received {len(body)} byte(s)")

        # Start listening
        print("start-listening {}", file=self.events_file)
        self.events_file.flush()

        # Write audio data
        with open(self.audio_file, "wb") as audio_file:
            audio_file.write(body)

        # Done listening
        print("stop-listening {}", file=self.events_file)
        self.events_file.flush()

        # Wait for response
        response = sys.stdin.buffer.readline().strip()

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(response)


# -----------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--audio-file", required=True, help="Path to write audio data")
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
    audio_file = args.audio_file
    events_file = open(args.events_file, "w")

    def make_server(*args, **kwargs):
        return Handler(audio_file, events_file, *args, **kwargs)

    http.server.HTTPServer((args.host, args.port), make_server).serve_forever()


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
