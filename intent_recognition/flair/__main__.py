#!/usr/bin/env python3
import os
import sys
import argparse
import logging

import jsonlines
import flair, torch
import pywrapfst as fst

from .flair_rhasspy import load_models, recognize, make_slot_fsts


# -------------------------------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser("flair_rhasspy")
    parser.add_argument(
        "--class-model", help="Path to intent classification model (final-model.pt)"
    )
    parser.add_argument(
        "--ner-model",
        action="append",
        default=[],
        help="Path to named entity recognition (NER) model (final-model.pt)",
    )
    parser.add_argument(
        "--ner-model-dir",
        help="Directory with named entity recognition (NER) models (one directory per intent)",
    )
    parser.add_argument(
        "--intent-fst", help="Path to intent finite state transducer for slot FSTs"
    )
    parser.add_argument(
        "--lower", action="store_true", help="Automatically lower-case input text"
    )
    parser.add_argument(
        "--no-cuda",
        action="store_true",
        help="Force PyTorch to use CPU even if CUDA is available",
    )
    parser.add_argument(
        "--debug", action="store_true", help="Print DEBUG messages to console"
    )
    args, _ = parser.parse_known_args()

    if args.debug:
        logging.root.setLevel(logging.DEBUG)

    logging.debug(args)

    ner_model_paths = [p for p in args.ner_model]
    if args.ner_model_dir:
        for f_name in os.listdir(args.ner_model_dir):
            dir_path = os.path.join(args.ner_model_dir, f_name)
            if os.path.isdir(dir_path):
                ner_model_paths.append(os.path.join(dir_path, "final-model.pt"))

    logging.debug(ner_model_paths)

    if args.no_cuda:
        logging.info("Using CPU instead of GPU")
        flair.device = torch.device("cpu")

    # Load flair models
    class_model, ner_models = load_models(args.class_model, ner_model_paths)

    intent_to_slots = {}
    if args.intent_fst is not None:
        logging.debug(f"Loading intent FST from {args.intent_fst}")
        intent_fst = fst.Fst.read(args.intent_fst)
        intent_to_slots = make_slot_fsts(intent_fst)

    # Recognize lines from stdin
    try:
        for line in sys.stdin:
            line = line.strip()
            if len(line) == 0:
                continue

            logging.debug(line)

            try:
                # Try to interpret as JSON
                request = json.loads(line)
                line = request["text"]
            except:
                pass  # assume line is just text

            if args.lower:
                line = line.lower()

            intent = recognize(
                line, class_model, ner_models, intent_to_slots=intent_to_slots
            )

            # Output to stdout
            with jsonlines.Writer(sys.stdout) as out:
                out.write(intent)

            sys.stdout.flush()
    except KeyboardInterrupt:
        pass


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
