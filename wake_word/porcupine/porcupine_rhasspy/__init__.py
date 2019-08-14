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

from typing import List

from .porcupine import Porcupine

# -------------------------------------------------------------------------------------------------


def wait_for_wake_word(
    library: str,
    model: str,
    keyword: List[str],
    audio_file=None,
    events_file=None,
    sensitivity: List[float] = [],
    event_start: str = "start",
    event_stop: str = "start",
    event_detected: str = "detected",
    auto_start: bool = False,
    debug: bool = False,
):
    if audio_file:
        audio_file = open(audio_file, "rb")
    else:
        audio_file = sys.stdin.buffer

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

    logging.debug(
        f"Loaded porcupine (keywords={keyword}, sensitivities={sensitivities})"
    )

    logging.debug(
        f"Expecting sample rate={handle.sample_rate}, frame length={handle.frame_length}"
    )

    request_id = ""
    report_audio = False

    if events_file or auto_start:
        listening = False

        # Read thread
        def read_audio():
            nonlocal listening, handle, report_audio
            try:
                while True:
                    chunk = audio_file.read(chunk_size)
                    if len(chunk) > 0:
                        if listening:
                            if report_audio:
                                logger.debug("Receiving audio")
                                report_audio = False

                            # Process audio chunk
                            chunk = struct.unpack_from(chunk_format, chunk)
                            keyword_index = handle.process(chunk)

                            if keyword_index:
                                if len(keyword) == 1:
                                    keyword_index = 0

                                logging.debug(f"Keyword {keyword_index} detected")
                                result = {
                                    "index": keyword_index,
                                    "keyword": keyword[keyword_index],
                                }

                                print(event_detected + request_id, end=" ")
                                with jsonlines.Writer(sys.stdout) as out:
                                    out.write(result)

                                sys.stdout.flush()
                    else:
                        time.sleep(0.01)
            except Exception as e:
                logging.exception("read_audio")

        threading.Thread(target=read_audio, daemon=True).start()

        if auto_start:
            logging.debug("Automatically started listening")
            listening = True
            report_audio = True

        if events_file:
            # Wait for start/stop events
            with open(events_file, "r") as events:
                while True:
                    line = events.readline().strip()
                    if len(line) == 0:
                        continue

                    logging.debug(line)
                    topic, event = line.split(" ", maxsplit=1)
                    if topic.startswith(event_start):
                        # Everything after expected topic is request id
                        request_id = topic[len(event_start) :]

                        # Clear buffer and start reading
                        listening = True
                        report_audio = True
                        logging.debug(f"Started listening (request_id={request_id})")
                    elif topic.startswith(event_stop):
                        # Everything after expected topic is request id
                        request_id = topic[len(event_start) :]

                        # Stop reading and transcribe
                        listening = False
                        logging.debug(f"Stopped listening (request_id={request_id})")

        else:
            # Wait forever
            threading.Event().wait()

    else:
        # Read all data from audio file, process, and stop
        audio_data = audio_file.read()
        while len(audio_data) > 0:
            chunk = audio_data[:chunk_size]
            audio_data = audio_data[chunk_size:]

            if len(chunk) == chunk_size:
                # Process audio chunk
                chunk = struct.unpack_from(chunk_format, chunk)
                keyword_index = handle.process(chunk)

                if keyword_index:
                    if len(keyword) == 1:
                        keyword_index = 0

                    logging.debug(f"Keyword {keyword_index} detected")
                    result = {"index": keyword_index, "keyword": keyword[keyword_index]}

                    print(event_detected + request_id, end=" ")
                    with jsonlines.Writer(sys.stdout) as out:
                        out.write(result)


# -------------------------------------------------------------------------------------------------


if __name__ == "__main__":
    main()
