#!/usr/bin/env python3
import sys
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic-file", required=True, help="File to write topic to")
    parser.add_argument(
        "--chunk-size",
        type=int,
        help="Number of bytes to read from stdin at a time",
        default=1024,
    )
    args = parser.parse_args()

    # Read topic
    with open(args.topic_file, "wb") as topic_file:
        while True:
            b = sys.stdin.buffer.read(1)
            if b == b" ":
                break

            topic_file.write(b)

    # Write remainder of stdin
    chunk = sys.stdin.buffer.read(args.chunk_size)

    while len(chunk) > 0:
        sys.stdout.buffer.write(chunk)
        sys.stdout.buffer.flush()
        chunk = sys.stdin.buffer.read(args.chunk_size)


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
