#!/usr/bin/env python3
import sys
import argparse
import logging

import webrtcvad


def main():
    parser = argparse.ArgumentParser("webrtcvad")
    parser.add_argument(
        "--chunk_size",
        help="Number of bytes to process at a time (default=960)",
        type=int,
        default=960,
    )
    parser.add_argument(
        "--sample_rate",
        help="Sample rate of audio data (default=16000)",
        type=int,
        default=16000,
    )
    parser.add_argument(
        "--vad_mode",
        help="Sensitivity (1-3, 3 is most sensitive, default=1)",
        type=int,
        default=1,
    )
    parser.add_argument(
        "--voice_text",
        help="Text to print when voice is detected (default=!)",
        default="!",
    )
    parser.add_argument(
        "--silence_text",
        help="Text to print when silence is detected (default=.)",
        default=".",
    )
    parser.add_argument(
        "--repeat", action="store_true", help="Repeat voice/silence text for each chunk"
    )
    parser.add_argument(
        "--debug", action="store_true", help="Print DEBUG messages to standard out"
    )

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    logging.debug(args)

    # Verify settings
    assert args.vad_mode in range(1, 4), f"VAD mode must be 1-3 (got {args.vad_mode})"

    chunk_ms = 1000 * ((args.chunk_size / 2) / args.sample_rate)
    assert chunk_ms in [
        10,
        20,
        30,
    ], f"Sample rate and chunk size must make for 10, 20, or 30 ms buffer sizes, assuming 16-bit mono audio (got {chunk_ms} ms)"

    # Detect voice
    vad = webrtcvad.Vad()
    vad.set_mode(args.vad_mode)

    # Read from stdin
    last_state = None
    while True:
        audio_data = sys.stdin.buffer.read(args.chunk_size)
        is_speech = vad.is_speech(audio_data, args.sample_rate)
        if args.repeat or (is_speech != last_state):
            if is_speech:
                print(args.voice_text, flush=True)
            else:
                print(args.silence_text, flush=True)

            last_state = is_speech


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
