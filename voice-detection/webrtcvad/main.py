#!/usr/bin/env python3
import sys
import argparse
import logging
import math
import jsonlines

import webrtcvad


def main():
    parser = argparse.ArgumentParser("webrtcvad")
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
        "--chunk-size",
        help="Number of bytes to process at a time (default=960)",
        type=int,
        default=960,
    )
    parser.add_argument(
        "--vad-mode",
        help="Sensitivity (1-3, 3 is most sensitive, default=1)",
        type=int,
        default=1,
    )
    parser.add_argument(
        "--min-seconds",
        help="Minimum number of seconds a voice command must last (default=2)",
        type=float,
        default=2,
    )
    parser.add_argument(
        "--max-seconds",
        help="Maximum number of seconds a voice command can last before timeout (default=30)",
        type=float,
        default=30,
    )
    parser.add_argument(
        "--speech-seconds",
        help="Seconds of speech before voice command is considered started (default=0.3)",
        type=float,
        default=0.3,
    )
    parser.add_argument(
        "--silence-seconds",
        help="Seconds of silence before voice command is considered stopped (default=0.5)",
        type=float,
        default=0.5,
    )
    parser.add_argument(
        "--event-start",
        help="Topic to start reading audio data (default=start)",
        default="start",
    )
    parser.add_argument(
        "--event-speech",
        help="Topic when speech is detected (default=speech)",
        default="speech",
    )
    parser.add_argument(
        "--event-silence",
        help="Topic when silence is detected (default=silence)",
        default="silence",
    )
    parser.add_argument(
        "--event-command-start",
        help="Topic when voice command starts (default=command-start)",
        default="command-start",
    )
    parser.add_argument(
        "--event-command-stop",
        help="Topic when voice command stops (default=command-stop)",
        default="command-stop",
    )
    parser.add_argument(
        "--event-command-timeout",
        help="Topic when voice command times out (default=command-timeout)",
        default="command-timeout",
    )
    parser.add_argument(
        "--debug", action="store_true", help="Print DEBUG messages to standard out"
    )

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    logging.debug(args)

    audio_file = sys.stdin.buffer
    if args.audio_file:
        audio_file = open(args.audio_file, "r")

    def send_event(topic, payload):
        print(topic, end=" ")

        with jsonlines.Writer(sys.stdout) as out:
            out.write(payload)

        sys.stdout.flush()

    # Verify settings
    sample_rate = 16000
    assert args.vad_mode in range(1, 4), f"VAD mode must be 1-3 (got {args.vad_mode})"

    chunk_ms = 1000 * ((args.chunk_size / 2) / sample_rate)
    assert chunk_ms in [
        10,
        20,
        30,
    ], f"Sample rate and chunk size must make for 10, 20, or 30 ms buffer sizes, assuming 16-bit mono audio (got {chunk_ms} ms)"

    # Voice detector
    vad = webrtcvad.Vad()
    vad.set_mode(args.vad_mode)

    # Pre-compute values
    seconds_per_buffer = args.chunk_size / sample_rate
    speech_buffers = int(math.ceil(args.speech_seconds / seconds_per_buffer))

    # Processes one voice command
    def read_audio():
        # State
        max_buffers = int(math.ceil(args.max_seconds / seconds_per_buffer))
        min_phrase_buffers = int(math.ceil(args.min_seconds / seconds_per_buffer))

        speech_buffers_left = speech_buffers
        is_speech = False
        last_speech = False
        in_phrase = False
        after_phrase = False
        buffer_count = 0

        finished = False
        timeout = False

        current_seconds = 0

        while True:
            chunk = audio_file.read(args.chunk_size)
            if len(chunk) < args.chunk_size:
                break  # TODO: buffer instead of bailing

            buffer_count += 1
            current_seconds += seconds_per_buffer

            # Check maximum number of seconds to record
            max_buffers -= 1
            if max_buffers <= 0:
                # Timeout
                logging.warn("Timeout")
                send_event(args.event_command_timeout, {"seconds": current_seconds})
                break

            # Detect speech in chunk
            is_speech = vad.is_speech(chunk, sample_rate)
            if is_speech and not last_speech:
                # Silence -> speech
                send_event(args.event_speech, {"seconds": current_seconds})
            elif not is_speech and last_speech:
                # Speech -> silence
                send_event(args.event_silence, {"seconds": current_seconds})

            last_speech = is_speech

            # Handle state changes
            if is_speech and speech_buffers_left > 0:
                speech_buffers_left -= 1
            elif is_speech and not in_phrase:
                # Start of phrase
                logging.debug("Voice command started")
                send_event(args.event_command_start, {"seconds": current_seconds})

                in_phrase = True
                after_phrase = False
                min_phrase_buffers = int(
                    math.ceil(args.min_seconds / seconds_per_buffer)
                )
            elif in_phrase and (min_phrase_buffers > 0):
                # In phrase, before minimum seconds
                min_phrase_buffers -= 1
            elif not is_speech:
                # Outside of speech
                if not in_phrase:
                    # Reset
                    speech_buffers_left = speech_buffers
                elif after_phrase and (silence_buffers > 0):
                    # After phrase, before stop
                    silence_buffers -= 1
                elif after_phrase and (silence_buffers <= 0):
                    # Phrase complete
                    logging.debug("Voice command finished")
                    send_event(args.event_command_stop, {"seconds": current_seconds})
                    break
                elif in_phrase and (min_phrase_buffers <= 0):
                    # Transition to after phrase
                    after_phrase = True
                    silence_buffers = int(
                        math.ceil(args.silence_seconds / seconds_per_buffer)
                    )

    # -------------------------------------------------------------------------

    if args.events_file:
        # Wait for start event
        with open(args.events_file, "r") as events:
            while True:
                line = events.readline().strip()
                if len(line) == 0:
                    continue

                logging.debug(line)
                topic, event = line.split(" ", maxsplit=1)
                if topic == args.event_start:
                    # Process voice command
                    logging.debug("Started listening")
                    read_audio()
    else:
        # Process a voice command immediately
        read_audio()


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
