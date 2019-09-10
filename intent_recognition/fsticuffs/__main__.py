#!/usr/bin/env python3
import logging

logger = logging.getLogger("fsticuffs")

import os
import sys
import argparse
import json
from typing import Optional, Dict, Any, Set

import jsonlines
import pywrapfst as fst

from intent_recognition.fsticuffs.fsticuffs import (
    recognize,
    empty_intent,
    fst_to_graph,
    recognize_fuzzy,
)

# -------------------------------------------------------------------------------------------------
# MQTT Events
# -------------------------------------------------------------------------------------------------

EVENT_PREFIX = "rhasspy/intent-recognition/"

# Input
EVENT_RECOGNIZE = EVENT_PREFIX + "recognize-intent"
EVENT_RELOAD = EVENT_PREFIX + "reload"

# Output
EVENT_ERROR = EVENT_PREFIX + "error"
EVENT_RECOGNIZED = EVENT_PREFIX + "intent-recognized"
EVENT_RELOADED = EVENT_PREFIX + "reloaded"

# -------------------------------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser("fsticuffs")
    parser.add_argument(
        "--intent-fst", help="Path to intent finite state transducer", required=True
    )
    parser.add_argument(
        "--skip-unknown",
        action="store_true",
        help="Skip tokens not present in FST input symbol table",
    )
    parser.add_argument(
        "--lower", action="store_true", help="Automatically lower-case input text"
    )
    parser.add_argument(
        "--fuzzy", action="store_true", help="Use fuzzy search (slower)"
    )
    parser.add_argument(
        "--stop-words",
        help="File with words that can be ignored during fuzzy recognition",
    )
    parser.add_argument(
        "--events-in-file",
        help="File to read events from (one per line, topic followed by JSON)",
        default=None,
    )
    parser.add_argument(
        "--events-out-file",
        help="File to write events to (one per line, topic followed by JSON)",
        default=None,
    )
    parser.add_argument(
        "--text-input",
        action="store_true",
        help="Input is text instead of topic + JSON",
    )
    parser.add_argument(
        "--debug", action="store_true", help="Print DEBUG messages to console"
    )

    args, rest = parser.parse_known_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    logger.debug(args)

    # -------------------------------------------------------------------------

    # File to read events from
    events_in_file = sys.stdin
    if args.events_in_file and (args.events_in_file != "-"):
        events_in_file = open(args.events_in_file, "r")

    # File to write events to
    events_out_file = sys.stdout
    if args.events_out_file and (args.events_out_file != "-"):
        events_out_file = open(args.events_out_file, "w")

    def send_event(topic, payload_dict={}):
        print(topic, end=" ", file=events_out_file)
        with jsonlines.Writer(events_out_file) as out:
            out.write(payload_dict)

        events_out_file.flush()

    # -------------------------------------------------------------------------

    intent_fst = None
    known_tokens = set()
    intent_graph = None
    stop_words = set()

    def reload_fst():
        nonlocal intent_fst, known_tokens, intent_graph, stop_words

        # Load intent fst
        intent_fst = fst.Fst.read(args.intent_fst)
        logger.debug(f"Loaded FST from {args.intent_fst}")

        # Add symbols from FST
        if args.skip_unknown:
            # Ignore words outside of input symbol table
            known_tokens = set()
            in_symbols = intent_fst.input_symbols()
            for i in range(in_symbols.num_symbols()):
                token = in_symbols.find(i).decode()
                if not (token.startswith("__") or token.startswith("<")):
                    known_tokens.add(token)

            logger.debug(f"Skipping words outside of set: {known_tokens}")

        intent_graph = None
        stop_words = set()
        if args.fuzzy:
            logger.debug("Fuzzy search enabled")
            intent_graph = fst_to_graph(intent_fst)

            # Load stop words (words that act like wildcards for transitions)
            if args.stop_words:
                with open(args.stop_words, "r") as stop_words_file:
                    stop_words = set([line.strip() for line in stop_words_file])

    # Initial load
    reload_fst()

    # Recognize lines from file
    for line in events_in_file:
        line = line.strip()
        logger.debug(line)

        try:
            if args.text_input:
                # Assume text input
                topic = EVENT_RECOGNIZE
                event = json.dumps({"text": line})
            else:
                # Expected <topic> <payload> on each line
                topic, event = line.split(" ", maxsplit=1)

            topic_parts = topic.split("/")
            base_topic = "/".join(topic_parts[:3])

            # Everything after base topic is request id
            request_id = "/".join(topic_parts[3:])
            if len(request_id) > 0:
                request_id = "/" + request_id

            if base_topic == EVENT_RECOGNIZE:
                event_dict = maybe_object(event)
                text = event_dict.get("text", "")

                if args.lower:
                    text = text.lower()

                if args.fuzzy:
                    # Fuzzy search
                    intent = recognize_fuzzy(
                        intent_graph,
                        text,
                        known_tokens=known_tokens,
                        stop_words=stop_words,
                    )
                else:
                    # Fast (strict) search
                    intent = recognize(intent_fst, text, known_tokens)

                send_event(EVENT_RECOGNIZED + request_id, intent)
            elif base_topic == EVENT_RELOAD:
                logging.debug("Reloading intent FST")

                event_dict = maybe_object(event)
                args.intent_fst = event_dict.get("intent-fst", args.intent_fst)
                reload_fst()

                send_event(EVENT_RELOADED + request_id, event_dict)
        except Exception as e:
            logger.exception(line)
            send_event(EVENT_ERROR, {"error": str(e)})


# -------------------------------------------------------------------------------------------------


def maybe_object(json_str):
    try:
        return json.loads(json_str)
    except:
        return {}


# -------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    main()
