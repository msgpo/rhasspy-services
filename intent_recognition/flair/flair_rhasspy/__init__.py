#!/usr/bin/env python3
import os
import logging
import subprocess
import time
from typing import Dict, Tuple, Any, Optional, List

import pywrapfst as fst
from flair.data import Sentence
from flair.models import TextClassifier, SequenceTagger

from jsgf2fst import fstaccept

logger = logging.getLogger("flair_rhasspy")

# -------------------------------------------------------------------------------------------------


def recognize(
    text: str,
    class_model: Optional[TextClassifier] = None,
    ner_models: Dict[str, SequenceTagger] = {},
    intent_name: Optional[str] = None,
    intent_to_slots: Dict[str, Dict[str, fst.Fst]] = {},
) -> Dict[str, Any]:
    intent = empty_intent()
    intent["text"] = text

    start_time = time.time()
    sentence = Sentence(text)

    if class_model is not None:
        class_model.predict(sentence)
        assert len(sentence.labels) > 0, "No intent predicted"

        label = sentence.labels[0]
        intent_id = label.value
        intent["intent"]["confidence"] = label.score
    elif len(ner_models) > 0:
        # Assume first intent
        intent_id = intent_name or next(iter(ner_models.keys()))
        intent["intent"]["confidence"] = 1
    else:
        return intent  # empty

    intent["intent"]["name"] = intent_id

    if intent_id in ner_models:
        slot_fsts = intent_to_slots.get(intent_id, {})

        # Predict entities
        ner_models[intent_id].predict(sentence)
        ner_dict = sentence.to_dict(tag_type="ner")
        for named_entity in ner_dict["entities"]:
            slot_name = named_entity["type"]
            slot_value = named_entity["text"]

            # Check for FST to transform
            slot_fst = slot_fsts.get(slot_name)
            if slot_fst is not None:
                try:
                    # Transform with FST
                    logger.debug(
                        f'Transforming "{slot_value}" for slot "{slot_name}" with FST'
                    )
                    slot_value = fstaccept(slot_fst, slot_value)[0]["text"]
                except:
                    logger.exception(slot_name)

            intent["entities"].append(
                {
                    "entity": slot_name,
                    "value": slot_value,
                    "raw_value": named_entity["text"],
                    "start": named_entity["start_pos"],
                    "end": named_entity["end_pos"],
                    "confidence": named_entity["confidence"],
                }
            )

    # Add slots
    intent["slots"] = {}
    for ev in intent["entities"]:
        intent["slots"][ev["entity"]] = ev["value"]

    # Record recognition time
    intent["recognize_seconds"] = time.time() - start_time

    return intent


# -------------------------------------------------------------------------------------------------


def load_models(
    class_model_path: Optional[str] = None, ner_model_paths: List[str] = []
) -> Tuple[Optional[TextClassifier], Dict[str, SequenceTagger]]:

    # Only load intent classifier if there is more than one intent
    class_model = None
    if (class_model_path is not None) and os.path.exists(class_model_path):
        logger.debug(f"Loading classification model from {class_model_path}")
        class_model = TextClassifier.load_from_file(class_model_path)
        logger.debug("Loaded classification model")

    ner_models = {}
    for ner_model_path in ner_model_paths:
        # Assume directory name is intent name
        intent_name = os.path.split(os.path.split(ner_model_path)[0])[1]
        logger.debug(
            f"Loading NER model from {ner_model_path} for intent {intent_name}"
        )
        ner_models[intent_name] = SequenceTagger.load_from_file(ner_model_path)

    logger.debug("Loaded NER model(s)")

    return class_model, ner_models


# -------------------------------------------------------------------------------------------------


def make_slot_fsts(intent_fst: fst.Fst) -> Dict[str, Dict[str, fst.Fst]]:
    out_symbols = intent_fst.output_symbols()
    intent_to_slots: Dict[str, Dict[str, fst.Fst]] = {}

    start_state = intent_fst.start()
    for intent_arc in intent_fst.arcs(start_state):
        # Extract intent name from output label
        intent_label = out_symbols.find(intent_arc.olabel).decode()
        assert intent_label.startswith("__label__"), intent_label
        intent_name = intent_label[9:]

        # Create mapping from slot (tag) name to acceptor FST
        slot_to_fst: Dict[str, fst.Fst] = {}
        intent_to_slots[intent_name] = slot_to_fst

        _make_slot_fst(intent_arc.nextstate, intent_fst, slot_to_fst)

    return intent_to_slots


def _make_slot_fst(state: int, intent_fst: fst.Fst, slot_to_fst: Dict[str, fst.Fst]):
    out_symbols = intent_fst.output_symbols()
    one_weight = fst.Weight.One(intent_fst.weight_type())

    for arc in intent_fst.arcs(state):
        label = out_symbols.find(arc.olabel).decode()
        if label.startswith("__begin__"):
            slot_name = label[9:]

            # Big assumption here that each instance of a slot (e.g., location)
            # will produce the same FST, and therefore doesn't need to be
            # processed again.
            if slot_name in slot_to_fst:
                continue  # skip duplicate slots

            end_label = f"__end__{slot_name}"

            # Create new FST
            slot_fst = fst.Fst()
            slot_fst.set_input_symbols(intent_fst.input_symbols())
            slot_fst.set_output_symbols(intent_fst.output_symbols())

            start_state = slot_fst.add_state()
            slot_fst.set_start(start_state)
            q = [arc.nextstate]
            state_map = {arc.nextstate: start_state}

            # Copy states/arcs from intent FST until __end__ is found
            while len(q) > 0:
                q_state = q.pop()
                for q_arc in intent_fst.arcs(q_state):
                    slot_arc_label = out_symbols.find(q_arc.olabel).decode()
                    if slot_arc_label != end_label:
                        if not q_arc.nextstate in state_map:
                            state_map[q_arc.nextstate] = slot_fst.add_state()

                        # Create arc
                        slot_fst.add_arc(
                            state_map[q_state],
                            fst.Arc(
                                q_arc.ilabel,
                                q_arc.olabel,
                                one_weight,
                                state_map[q_arc.nextstate],
                            ),
                        )

                        # Continue copy
                        q.append(q_arc.nextstate)
                    else:
                        # Mark previous state as final
                        slot_fst.set_final(state_map[q_state])

            slot_to_fst[slot_name] = minimize_fst(slot_fst)

        # Recurse
        _make_slot_fst(arc.nextstate, intent_fst, slot_to_fst)


# -------------------------------------------------------------------------------------------------


def minimize_fst(the_fst: fst.Fst) -> fst.Fst:
    # BUG: Fst.minimize does not pass allow_nondet through, so we have to call out to the command-line
    minimize_cmd = ["fstminimize", "--allow_nondet"]
    return fst.Fst.read_from_string(
        subprocess.check_output(minimize_cmd, input=the_fst.write_to_string())
    )


# -------------------------------------------------------------------------------------------------


def empty_intent() -> Dict[str, Any]:
    return {
        "text": "",
        "intent": {"name": "", "confidence": 0},
        "entities": [],
        "intents": [],
        "slots": {},
        "recognize_seconds": 0.0,
    }
