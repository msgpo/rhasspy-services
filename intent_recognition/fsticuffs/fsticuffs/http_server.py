#!/usr/bin/env python3
import logging

logger = logging.getLogger("http_server")

import sys
import json
import http.server
import argparse

import jsonlines


class Handler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers["Content-Length"])
        body = self.rfile.read(content_length)
        request = json.loads(body)

        with jsonlines.Writer(sys.stdout) as out:
            out.write(request)

        sys.stdout.flush()

        # Wait for response
        response = sys.stdin.buffer.readline().strip()

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(response)


# -----------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser()
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

    try:
        http.server.HTTPServer((args.host, args.port), Handler).serve_forever()
    except KeyboardInterrupt:
        pass


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
