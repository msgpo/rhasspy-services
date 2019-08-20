#!/usr/bin/env python3
import logging

logger = logging.getLogger("porcupine_rhasspy")

import os
import sys
import jsonlines
import time
import argparse
import threading
import struct
from typing import List, BinaryIO, TextIO, Optional

from .porcupine import Porcupine

# -------------------------------------------------------------------------------------------------
# MQTT Events
# -------------------------------------------------------------------------------------------------

EVENT_PREFIX = "rhasspy/wake-word/"

# Input
EVENT_START = EVENT_PREFIX + "start-listening"
EVENT_STOP = EVENT_PREFIX + "stop-listening"
EVENT_RELOAD = EVENT_PREFIX + "reload"

# Output
EVENT_ERROR = EVENT_PREFIX + "error"
EVENT_STARTED = EVENT_PREFIX + "listening-started"
EVENT_STOPPED = EVENT_PREFIX + "listening-stopped"
EVENT_DETECTED = EVENT_PREFIX + "detected"
EVENT_RECEIVING_AUDIO = EVENT_PREFIX + "receiving-audio"
EVENT_RELOADED = EVENT_PREFIX + "reloaded"

# -------------------------------------------------------------------------------------------------


def wait_for_wake_word(
    audio_file: BinaryIO,
    events_out_file: TextIO,
    library: str,
    model: str,
    keyword: List[str],
    events_in_file: Optional[TextIO] = None,
    sensitivity: List[float] = [],
    auto_start: bool = False,
):
    def send_event(topic, payload_dict={}, show_event=True):
        if show_event:
            print(topic, end=" ")

        with jsonlines.Writer(events_out_file) as out:
            out.write(payload_dict)

        events_out_file.flush()

    # Ensure each keyword has a sensitivity value
    sensitivities = sensitivity
    while len(sensitivities) < len(keyword):
        sensitivities.append(0.5)

    # Load porcupine
    handle = Porcupine(
        library, model, keyword_file_paths=keyword, sensitivities=sensitivities
    )

    chunk_size = handle.frame_length * 2
    chunk_format = "h" * handle.frame_length

    logger.debug(
        f"Loaded porcupine (keywords={keyword}, sensitivities={sensitivities})"
    )

    logger.debug(
        f"Expecting sample rate={handle.sample_rate}, frame length={handle.frame_length}"
    )

    request_id = ""
    report_audio = False

    if events_in_file:
        listening = False

        # Read thread
        def read_audio():
            nonlocal listening, handle, report_audio
            try:
                while True:
                    chunk = audio_file.read(chunk_size)
                    if len(chunk) == chunk_size:
                        if listening:
                            if report_audio:
                                logger.debug("Receiving audio")
                                send_event(EVENT_RECEIVING_AUDIO + request_id)
                                report_audio = False

                            # Process audio chunk
                            chunk = struct.unpack_from(chunk_format, chunk)
                            keyword_index = handle.process(chunk)

                            if keyword_index:
                                if len(keyword) == 1:
                                    keyword_index = 0

                                if keyword_index >= 0:
                                    logger.debug(f"Keyword {keyword_index} detected")
                                    result = {
                                        "index": keyword_index,
                                        "keyword": keyword[keyword_index],
                                    }

                                    send_event(EVENT_DETECTED + request_id, result)
                    else:
                        # Prevent 100% CPU usage
                        time.sleep(0.01)
            except Exception as e:
                logger.exception("read_audio")

        threading.Thread(target=read_audio, daemon=True).start()

        if auto_start:
            logger.debug("Automatically started listening")
            listening = True
            report_audio = True

        # Process events
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
                    # Clear buffer and start reading
                    listening = True
                    report_audio = True
                    logger.debug(f"Started listening (request_id={request_id})")
                    send_event(EVENT_STARTED + request_id)
                elif base_topic == EVENT_STOP:
                    # Stop reading and transcribe
                    listening = False
                    logger.debug(f"Stopped listening (request_id={request_id})")
                    send_event(EVENT_STOPPED + request_id)
                elif base_topic == EVENT_RELOAD:
                    logger.debug("Reloading keyword(s)")
                    event_dict = maybe_object(event)

                    keyword = event_dict.get("keyword", keyword)
                    if isinstance(keyword, str):
                        keyword = [keyword]

                    # Load porcupine
                    handle = Porcupine(
                        library,
                        model,
                        keyword_file_paths=keyword,
                        sensitivities=sensitivities,
                    )
                    send_event(EVENT_RELOADED + request_id, event_dict)
            except Exception as e:
                logger.exception(line)
                send_event(EVENT_ERROR + request_id, {"error": str(e)})
    else:
        # Read all data from audio file, process, and stop
        chunk = audio_file.read(chunk_size)
        while len(chunk) == chunk_size:
            # Process audio chunk
            chunk = struct.unpack_from(chunk_format, chunk)
            keyword_index = handle.process(chunk)

            if keyword_index:
                if len(keyword) == 1:
                    keyword_index = 0

                if keyword_index >= 0:
                    logger.debug(f"Keyword {keyword_index} detected")
                    result = {"index": keyword_index, "keyword": keyword[keyword_index]}
                    send_event(EVENT_DETECTED, result, show_event=False)

            chunk = audio_file.read(chunk_size)


# -------------------------------------------------------------------------------------------------


def maybe_object(json_str):
    try:
        return json.loads(json_str)
    except:
        return {}


# -------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    main()
