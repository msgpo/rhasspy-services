#!/usr/bin/env python3
__version__ = "3.0"

import logging

logger = logging.getLogger("fsticuffs")

import re
from typing import Optional, Dict, Any, Set

import pywrapfst as fst
from jsgf2fst import fstaccept

# -------------------------------------------------------------------------------------------------


def recognize(
    intent_fst: fst.Fst, text: str, known_tokens: Optional[Set[str]] = None
) -> Dict[str, Any]:
    tokens = re.split("\s+", text)

    if known_tokens:
        # Filter tokens
        tokens = [t for t in tokens if t in known_tokens]

    # Only run acceptor if there are any tokens
    if len(tokens) > 0:
        intents = fstaccept(intent_fst, tokens)
    else:
        intents = []

    logger.debug(f"Recognized {len(intents)} intent(s)")

    # Use first intent
    if len(intents) > 0:
        intent = intents[0]

        # Add slots
        intent["slots"] = {}
        for ev in intent["entities"]:
            intent["slots"][ev["entity"]] = ev["value"]

        # Add alternative intents
        intent["intents"] = []
        for other_intent in intents[1:]:
            intent["intents"].append(other_intent)
    else:
        intent = empty_intent()
        intent["text"] = text

    return intent


# -------------------------------------------------------------------------------------------------


def empty_intent() -> Dict[str, Any]:
    return {
        "text": "",
        "intent": {"name": "", "confidence": 0},
        "entities": [],
        "intents": [],
        "slots": {},
    }
