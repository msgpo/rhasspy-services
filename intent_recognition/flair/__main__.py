#!/usr/bin/env python3
import os
import sys
import argparse
import json
import logging
import logging.config
logger = logging.getLogger("flair_rhasspy")

import jsonlines
import pywrapfst as fst

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
        "--text-input",
        action="store_true",
        help="Input is text instead of topic + JSON",
    )
    parser.add_argument(
        "--debug", action="store_true", help="Print DEBUG messages to console"
    )
    args, _ = parser.parse_known_args()

    if args.debug:
        logging.root.setLevel(logging.DEBUG)

    logger.debug(args)

    if (
        (args.class_model is None)
        and (args.ner_model_dir is None)
        and (len(args.ner_model) == 0)
    ):
        logger.fatal(
            "One of --class-model, --ner-model-dir, or --ner-model is required"
        )
        sys.exit(1)

    # -------------------------------------------------------------------------

    # Doing imports later because they're so slow (ensure --help is fast)
    import flair, torch
    from .flair_rhasspy import load_models, recognize, make_slot_fsts

    # Configure logging (flair screws with it)
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": True,
            "formatters": {
                "rhasspy.format": {"format": "%(levelname)s:%(name)s:%(message)s"}
            },
            "handlers": {
                "rhasspy.handler": {
                    "class": "logging.StreamHandler",
                    "formatter": "rhasspy.format",
                    "stream": "ext://sys.stderr",
                }
            },
            "loggers": {
                "flair_rhasspy": {"handlers": ["rhasspy.handler"], "propagate": False},
                "flair": {
                    "handlers": ["rhasspy.handler"],
                    "level": "INFO",
                    "propagate": False,
                },
            },
            "root": {"handlers": ["rhasspy.handler"]},
        }
    )

    if args.debug:
        logging.root.setLevel(logging.DEBUG)

    # Load intent FST
    if args.intent_fst is not None:
        logger.debug(f"Loading intent FST from {args.intent_fst}")
        intent_fst = fst.Fst.read(args.intent_fst)
        intent_to_slots = make_slot_fsts(intent_fst)
        logger.debug(
            "Intent slots: {}".format(
                {
                    name: list(slot_fsts.keys())
                    for name, slot_fsts in intent_to_slots.items()
                }
            )
        )

    # Load NER models
    ner_model_paths = [p for p in args.ner_model]
    if args.ner_model_dir:
        for f_name in os.listdir(args.ner_model_dir):
            dir_path = os.path.join(args.ner_model_dir, f_name)
            if os.path.isdir(dir_path):
                ner_model_paths.append(os.path.join(dir_path, "final-model.pt"))

    logger.debug(ner_model_paths)

    if args.no_cuda:
        logger.info("Using CPU instead of GPU")
        flair.device = torch.device("cpu")

    # Load flair models
    class_model, ner_models = load_models(args.class_model, ner_model_paths)

    # Recognize lines from stdin
    try:
        for line in sys.stdin:
            line = line.strip()
            if len(line) == 0:
                continue

            logger.debug(line)

            if args.text_input:
                pass
            else:
                request = json.loads(line)
                line = request["text"]

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
