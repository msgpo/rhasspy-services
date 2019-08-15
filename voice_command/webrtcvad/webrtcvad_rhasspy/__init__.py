#!/usr/bin/env python3
import logging

logger = logging.getLogger("webrtcvad_rhasspy")

import sys
import argparse
import math
import threading
import time
from queue import Queue
from typing import List, BinaryIO, TextIO, Optional

import jsonlines
import webrtcvad

# -------------------------------------------------------------------------------------------------
# MQTT Events
# -------------------------------------------------------------------------------------------------

EVENT_PREFIX = "rhasspy/voice-command/"

# Input
EVENT_START = EVENT_PREFIX + "start-listening"

# Output
EVENT_ERROR = EVENT_PREFIX + "error"
EVENT_SPEECH = EVENT_PREFIX + "speech"
EVENT_SILENCE = EVENT_PREFIX + "silence"
EVENT_STARTED = EVENT_PREFIX + "command-started"
EVENT_STOPPED = EVENT_PREFIX + "command-stopped"
EVENT_TIMEOUT = EVENT_PREFIX + "command-timeout"
EVENT_RECEIVNG_AUDIO = EVENT_PREFIX + "receiving-audio"

# -----------------------------------------------------------------------------


def wait_for_command(
    audio_file: BinaryIO,
    events_out_file: TextIO,
    events_in_file: Optional[TextIO] = None,
    vad_mode=3,
    sample_rate=16000,
    chunk_size=960,
    min_seconds=2,
    max_seconds=30,
    speech_seconds=0.3,
    silence_seconds=0.5,
):
    def send_event(topic, payload_dict={}):
        print(topic, end=" ")

        with jsonlines.Writer(events_out_file) as out:
            out.write(payload_dict)

        events_out_file.flush()

    # Verify settings
    sample_rate = 16000
    assert vad_mode in range(1, 4), f"VAD mode must be 1-3 (got {vad_mode})"

    chunk_ms = 1000 * ((chunk_size / 2) / sample_rate)
    assert chunk_ms in [10, 20, 30], (
        "Sample rate and chunk size must make for 10, 20, or 30 ms buffer sizes,"
        + f" assuming 16-bit mono audio (got {chunk_ms} ms)"
    )

    # Voice detector
    vad = webrtcvad.Vad()
    vad.set_mode(vad_mode)

    audio_chunks = Queue()
    report_audio = False
    request_id = ""

    # Pre-compute values
    seconds_per_buffer = chunk_size / sample_rate
    speech_buffers = int(math.ceil(speech_seconds / seconds_per_buffer))

    # Processes one voice command
    def process_audio(request_id=""):
        nonlocal audio_chunks

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
            chunk = audio_chunks.get()
            buffer_count += 1
            current_seconds += seconds_per_buffer

            # Check maximum number of seconds to record
            max_buffers -= 1
            if max_buffers <= 0:
                # Timeout
                logger.warn("Timeout")
                send_event(EVENT_TIMEOUT + request_id, {"seconds": current_seconds})
                break

            # Detect speech in chunk
            is_speech = vad.is_speech(chunk, sample_rate)
            if is_speech and not last_speech:
                # Silence -> speech
                send_event(EVENT_SPEECH + request_id, {"seconds": current_seconds})
            elif not is_speech and last_speech:
                # Speech -> silence
                send_event(EVENT_SILENCE + request_id, {"seconds": current_seconds})

            last_speech = is_speech

            # Handle state changes
            if is_speech and speech_buffers_left > 0:
                speech_buffers_left -= 1
            elif is_speech and not in_phrase:
                # Start of phrase
                logger.debug("Voice command started")
                send_event(EVENT_STARTED + request_id, {"seconds": current_seconds})

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
                    logger.debug("Voice command finished")
                    send_event(EVENT_STOPPED + request_id, {"seconds": current_seconds})
                    break
                elif in_phrase and (min_phrase_buffers <= 0):
                    # Transition to after phrase
                    after_phrase = True
                    silence_buffers = int(
                        math.ceil(silence_seconds / seconds_per_buffer)
                    )

    # -------------------------------------------------------------------------

    def read_audio():
        nonlocal audio_file, audio_chunks, report_audio, request_id
        try:
            while True:
                chunk = audio_file.read(chunk_size)
                if len(chunk) == chunk_size:
                    if report_audio:
                        logger.debug("Receiving audio")
                        send_event(EVENT_RECEIVNG_AUDIO + request_id)
                        report_audio = False

                    audio_chunks.put(chunk)
                else:
                    # Avoid 100% CPU usage
                    time.sleep(0.01)
        except Exception as e:
            logger.exception("read_audio")

    threading.Thread(target=read_audio, daemon=True).start()

    # -------------------------------------------------------------------------

    if events_in_file:
        # Wait for start event
        for line in events_in_file:
            line = line.strip()
            if len(line) == 0:
                continue

            logger.debug(line)

            try:
                # Expected <topic> <payload> on each line
                topic, event = line.split(" ", maxsplit=1)
                topic_parts = topic.split("/")
                base_topic = "/".join(topic_parts[:3])

                # Everything after base topic is request id
                request_id = "/".join(topic_parts[3:])
                if len(request_id) > 0:
                    request_id = "/" + request_id

                if base_topic == EVENT_START:
                    # Clear audio queue
                    with audio_chunks.mutex:
                        audio_chunks.queue.clear()

                    # Process voice command
                    logger.debug(f"Started listening (request_id={request_id})")
                    report_audio = True
                    process_audio(request_id)
            except Exception as e:
                logger.exception(line)
                send_event(EVENT_ERROR + request_id, {"error": str(e)})
    else:
        # Process a voice command immediately
        chunk = audio_file.read(chunk_size)
        while len(chunk) == chunk_size:
            audio_chunks.put(chunk)
            process_audio()
            chunk = audio_file.read(chunk_size)


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
