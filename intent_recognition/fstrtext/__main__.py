#!/usr/bin/env python3
import sys
import argparse
import re
import json
import logging

logger = logging.getLogger("fstrtext")

import pywrapfst as fst
import jsonlines

from training.jsgf2fst import (
    make_slot_acceptor,
    filter_words,
    apply_fst,
    longest_path,
    symbols2intent,
    fstprintall,
)


# -------------------------------------------------------------------------------------------------
# MQTT Events
# -------------------------------------------------------------------------------------------------

EVENT_PREFIX = "rhasspy/intent-recognition/"

# Input
EVENT_RECOGNIZE = EVENT_PREFIX + "recognize-intent"

# Output
EVENT_ERROR = EVENT_PREFIX + "error"
EVENT_RECOGNIZED = EVENT_PREFIX + "intent-recognized"

# -------------------------------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--slot-fst", required=True, help="Path to write slot acceptor")
    parser.add_argument(
        "--classifier-sentences",
        required=True,
        help="File to write out classifier sentences",
    )
    parser.add_argument(
        "--classifier-labels", required=True, help="File to read classifier labels"
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
        "--lower", action="store_true", help="Automatically lower-case input text"
    )
    parser.add_argument(
        "--text-input",
        action="store_true",
        help="Input is text instead of event topic + JSON",
    )
    parser.add_argument(
        "--debug", action="store_true", help="Print DEBUG messages to console"
    )

    args, _ = parser.parse_known_args()

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

    # Files used to communicate with classifier
    classifier_sentences = open(args.classifier_sentences, "w")
    classifier_labels = open(args.classifier_labels, "r")

    # FST used to recognize slot values
    slot_fst = fst.Fst.read(args.slot_fst)
    logging.debug(f"Loaded slot FST from {args.slot_fst}")

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

                # Send text to classifier
                print(text, file=classifier_sentences)
                classifier_sentences.flush()

                # Read predicted label back from classifier.
                # Assume __label__ prefix.
                label = classifier_labels.readline().strip()
                logger.debug(label)

                # Strip __label__ prefix
                intent_name = label[9:]

                # Create filtered sentence with label
                words = [label] + filter_words(re.split(r"\s+", text), slot_fst)

                try:
                    # Run sentence through slot FST
                    words_fst = apply_fst(words, slot_fst)

                    # Assume the longest path through the FST is the correct one.
                    # We're assuming more recognized slots are better.
                    path_fst = longest_path(words_fst)
                    path_words = fstprintall(path_fst, exclude_meta=False)[0]
                except Exception as e:
                    logger.exception("apply_fst")

                    # Just use original words
                    path_words = words

                # Convert recognized sentence to intent
                intent = symbols2intent(path_words)
                intent["intent"]["name"] = intent_name

                send_event(EVENT_RECOGNIZED + request_id, intent)

        except Exception as e:
            logger.exception(line)
            send_event(EVENT_ERROR, {"error": str(e)})


# -----------------------------------------------------------------------------


def maybe_object(json_str):
    try:
        return json.loads(json_str)
    except:
        return {}


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
