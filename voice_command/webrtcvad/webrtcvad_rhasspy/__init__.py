#!/usr/bin/env python3
import logging

logger = logging.getLogger("webrtcvad_rhasspy")

import sys
import argparse
import math
import jsonlines

import webrtcvad

# -----------------------------------------------------------------------------


def wait_for_command(
    audio_file=None,
    events_file=None,
    vad_mode=3,
    sample_rate=16000,
    chunk_size=960,
    min_seconds=2,
    max_seconds=30,
    speech_seconds=0.3,
    silence_seconds=0.5,
    event_start="start",
    event_speech="speech",
    event_silence="silence",
    event_command_start="command-start",
    event_command_stop="command-stop",
    event_command_timeout="command-timeout",
    debug=False,
):
    if audio_file:
        audio_file = open(audio_file, "r")
    else:
        audio_file = sys.stdin.buffer

    def send_event(topic, payload):
        print(topic, end=" ")

        with jsonlines.Writer(sys.stdout) as out:
            out.write(payload)

        sys.stdout.flush()

    # Verify settings
    sample_rate = 16000
    assert vad_mode in range(1, 4), f"VAD mode must be 1-3 (got {vad_mode})"

    chunk_ms = 1000 * ((chunk_size / 2) / sample_rate)
    assert chunk_ms in [
        10,
        20,
        30,
    ], f"Sample rate and chunk size must make for 10, 20, or 30 ms buffer sizes, assuming 16-bit mono audio (got {chunk_ms} ms)"

    # Voice detector
    vad = webrtcvad.Vad()
    vad.set_mode(vad_mode)

    # Pre-compute values
    seconds_per_buffer = chunk_size / sample_rate
    speech_buffers = int(math.ceil(speech_seconds / seconds_per_buffer))

    # Processes one voice command
    def read_audio():
        # State
        max_buffers = int(math.ceil(max_seconds / seconds_per_buffer))
        min_phrase_buffers = int(math.ceil(min_seconds / seconds_per_buffer))

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
            chunk = audio_file.read(chunk_size)
            if len(chunk) < chunk_size:
                break  # TODO: buffer instead of bailing

            buffer_count += 1
            current_seconds += seconds_per_buffer

            # Check maximum number of seconds to record
            max_buffers -= 1
            if max_buffers <= 0:
                # Timeout
                logging.warn("Timeout")
                send_event(event_command_timeout, {"seconds": current_seconds})
                break

            # Detect speech in chunk
            is_speech = vad.is_speech(chunk, sample_rate)
            if is_speech and not last_speech:
                # Silence -> speech
                send_event(event_speech, {"seconds": current_seconds})
            elif not is_speech and last_speech:
                # Speech -> silence
                send_event(event_silence, {"seconds": current_seconds})

            last_speech = is_speech

            # Handle state changes
            if is_speech and speech_buffers_left > 0:
                speech_buffers_left -= 1
            elif is_speech and not in_phrase:
                # Start of phrase
                logging.debug("Voice command started")
                send_event(event_command_start, {"seconds": current_seconds})

                in_phrase = True
                after_phrase = False
                min_phrase_buffers = int(math.ceil(min_seconds / seconds_per_buffer))
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
                    send_event(event_command_stop, {"seconds": current_seconds})
                    break
                elif in_phrase and (min_phrase_buffers <= 0):
                    # Transition to after phrase
                    after_phrase = True
                    silence_buffers = int(
                        math.ceil(silence_seconds / seconds_per_buffer)
                    )

    # -------------------------------------------------------------------------

    if events_file:
        # Wait for start event
        with open(events_file, "r") as events:
            while True:
                line = events.readline().strip()
                if len(line) == 0:
                    continue

                logging.debug(line)
                topic, event = line.split(" ", maxsplit=1)
                if topic == event_start:
                    # Process voice command
                    logging.debug("Started listening")
                    read_audio()
    else:
        # Process a voice command immediately
        read_audio()


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
