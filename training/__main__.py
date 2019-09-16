#!/usr/bin/env python3
import os
import re
import sys
import argparse
import logging
from pathlib import Path
from typing import Dict, Set, Iterable
from collections import deque

import yaml
import pydash
import pywrapfst as fst
import doit
from doit import create_after

from training.jsgf2fst import (
    get_grammar_dependencies,
    grammar_to_fsts,
    slots_to_fsts,
    make_intent_fst,
)

from training.ini_jsgf import make_grammars
from training.vocab_dict import make_dict

logger = logging.getLogger("rhasspy_train")
logging.basicConfig(level=logging.DEBUG)

# -----------------------------------------------------------------------------


def env_constructor(loader, node):
    """Expands !env STRING to replace environment variables in STRING."""
    return os.path.expandvars(node.value)


yaml.SafeLoader.add_constructor("!env", env_constructor)

# -----------------------------------------------------------------------------

# Profile directory
profile_dir = Path(os.getenv("profile_dir", os.getcwd()))
os.putenv("profile_dir", str(profile_dir))
logger.debug(f"Profile at {profile_dir}")

# Load profile
profile_yaml = profile_dir / "profile.yml"

with open(profile_yaml, "r") as profile_file:
    profile = yaml.safe_load(profile_file)


# Get default values
def ppath(query: str, default: str) -> Path:
    return Path(pydash.get(profile, query, profile_dir / Path(default)))


# Inputs
intent_whitelist = ppath("training.intent-whitelist", "intent_whitelist")
sentences_ini = ppath("training.sentences-file", "sentences.ini")
base_dictionary = ppath("training.base-dictionary", "base_dictionary.txt")
base_language_model = ppath("training.base-language-model", "base_language_model.txt")
base_language_model_fst = ppath(
    "training.base-language-model-fst", "base_language_model.fst"
)
base_language_model_weight = pydash.get(
    profile, "training.base-language-model-weight", None
)
custom_words = ppath("training.custom-words-file", "custom_words.txt")
g2p_model = ppath("training.grapheme-to-phoneme-model", "g2p.fst")
kaldi_dir = Path(os.getenv("kaldi_dir") or "/opt/kaldi")
kaldi_model_dir = ppath("training.kaldi.model-directory", "model")
kaldi_graph_dir = ppath("training.kaldi.graph-directory", "model/graph")
kaldi_model_type = pydash.get(profile, "training.kaldi.model-type", None)

# Outputs
dictionary = ppath("training.dictionary", "dictionary.txt")
language_model = ppath("training.language-model", "language_model.txt")
intent_fst = ppath("training.intent-fst", "intent.fst")
vocab = ppath("training.vocabulary-file", "vocab.txt")
unknown_words = ppath("training.unknown-words-file", "unknown.txt")
guess_words = ppath("training.guess-words-file", "guess_words.json")
grammar_dir = ppath("training.grammar-directory", "grammars")
fsts_dir = ppath("training.fsts-directory", "fsts")
slots_dir = ppath("training.slots-directory", "slots")

# -----------------------------------------------------------------------------

# Create cache directories
for dir_path in [grammar_dir, fsts_dir]:
    dir_path.mkdir(parents=True, exist_ok=True)

# -----------------------------------------------------------------------------

# Set of used intents
intents: Set[str] = set()

# -----------------------------------------------------------------------------


def task_grammars():
    """Transforms sentences.ini into JSGF grammars, one per intent."""
    maybe_deps = []
    whitelist = None

    # Default to using all intents
    intents.update(_get_intents(sentences_ini))

    # Check if intent whitelist exists
    if intent_whitelist.exists():
        with open(intent_whitelist, "r") as whitelist_file:
            # Each line is an intent to use
            for line in whitelist_file:
                line = line.strip()
                if len(line) > 0:
                    if whitelist is None:
                        whitelist = []
                        intents.clear()
                        maybe_deps.append(intent_whitelist)

                    whitelist.append(line)
                    intents.add(line)

    def ini_to_grammars(targets):
        with open(sentences_ini, "r") as sentences_file:
            make_grammars(sentences_file, grammar_dir, whitelist=whitelist)

    return {
        "file_dep": [sentences_ini] + maybe_deps,
        "targets": [grammar_dir / f"{intent}.gram" for intent in intents],
        "actions": [ini_to_grammars],
    }


# -----------------------------------------------------------------------------


def do_slots_to_fst(slot_names, targets):
    slot_fsts = slots_to_fsts(slots_dir, slot_names=slot_names)
    for slot_name, slot_fst in slot_fsts.items():
        # Slot name will already have "$"
        slot_fst.write(str(fsts_dir / f"{slot_name}.fst"))


def do_grammar_to_fsts(grammar_path: Path, replace_fst_paths: Dict[str, Path], targets):
    # Load dependent FSTs
    replace_fsts = {
        replace_name: fst.Fst.read(str(replace_path))
        for replace_name, replace_path in replace_fst_paths.items()
    }

    grammar = grammar_path.read_text()
    listener = grammar_to_fsts(grammar, replace_fsts=replace_fsts)
    grammar_name = listener.grammar_name

    # Write FST for each JSGF rule
    for rule_name, rule_fst in listener.fsts.items():
        fst_path = fsts_dir / f"{rule_name}.fst"
        rule_fst.write(str(fst_path))

    # Write FST for main grammar rule
    grammar_fst_path = fsts_dir / f"{grammar_name}.fst"
    listener.grammar_fst.write(str(grammar_fst_path))


# -----------------------------------------------------------------------------


@create_after(executed="grammars")
def task_grammar_fsts():
    """Creates grammar FSTs from JSGF grammars and relevant slots."""
    tasks = []
    used_slots: Set[str] = set()

    for intent in intents:
        grammar_path = grammar_dir / f"{intent}.gram"
        grammar = grammar_path.read_text()
        grammar_deps = get_grammar_dependencies(grammar)

        rule_names: Set[str] = set()
        replace_fst_paths: Dict[str, Path] = {}

        # Process dependencies
        for node, data in grammar_deps.graph.nodes(data=True):
            node_type = data["type"]

            if node_type == "slot":
                # Strip "$"
                slot_name = node[1:]
                used_slots.add(slot_name)

                # Path to slot FST
                replace_fst_paths[node] = fsts_dir / f"{node}.fst"
            elif node_type == "remote rule":
                # Path to rule FST
                replace_fst_paths[node] = fsts_dir / f"{node}.fst"
            elif node_type == "local rule":
                rule_names.add(node)

        # All rule/grammar FSTs that will be generated
        grammar_fst_paths = [fsts_dir / f"{rule_name}.fst" for rule_name in rule_names]
        grammar_fst_paths.append(fsts_dir / f"{intent}.fst")

        yield {
            "name": intent + "_fst",
            "file_dep": [grammar_path] + list(replace_fst_paths.values()),
            "targets": grammar_fst_paths,
            "actions": [(do_grammar_to_fsts, [grammar_path, replace_fst_paths])],
        }

    # slots -> FST
    yield {
        "name": "slot_fsts",
        "file_dep": [slots_dir / slot_name for slot_name in used_slots],
        "targets": [fsts_dir / f"${slot_name}.fst" for slot_name in used_slots],
        "actions": [(do_slots_to_fst, [used_slots])],
    }


# -----------------------------------------------------------------------------


def do_intent_fst(intents: Iterable[str], targets):
    intent_fsts = {
        intent: fst.Fst.read(str(fsts_dir / f"{intent}.fst")) for intent in intents
    }
    intent_fst = make_intent_fst(intent_fsts)
    intent_fst.write(targets[0])


@create_after(executed="grammars")
def task_intent_fst():
    """Merges grammar FSTs into single intent.fst."""
    return {
        "file_dep": [fsts_dir / f"{intent}.fst" for intent in intents],
        "targets": [intent_fst],
        "actions": [(do_intent_fst, [intents])],
    }


# -----------------------------------------------------------------------------


def task_language_model():
    """Creates an ARPA language model from intent.fst."""

    if base_language_model_weight is not None:
        yield {
            "name": "base_lm_to_fst",
            "file_dep": [base_language_model],
            "targets": [base_language_model_fst],
            "actions": ["ngramread --ARPA %(dependencies)s %(targets)s"],
        }

    # FST -> n-gram counts
    intent_counts = str(intent_fst) + ".counts"
    yield {
        "name": "intent_counts",
        "file_dep": [intent_fst],
        "targets": [intent_counts],
        "actions": ["ngramcount %(dependencies)s %(targets)s"],
    }

    # n-gram counts -> model
    intent_model = str(intent_fst) + ".model"
    yield {
        "name": "intent_model",
        "file_dep": [intent_counts],
        "targets": [intent_model],
        "actions": ["ngrammake %(dependencies)s %(targets)s"],
    }

    if base_language_model_weight is not None:
        merged_model = str(intent_model) + ".merge"

        # merge
        yield {
            "name": "lm_merge",
            "file_dep": [base_language_model_fst, intent_model],
            "targets": [merged_model],
            "actions": [
                f"ngrammerge --alpha={base_language_model_weight} %(dependencies)s %(targets)s"
            ],
        }

        intent_model = merged_model

    # model -> ARPA
    yield {
        "name": "intent_arpa",
        "file_dep": [intent_model],
        "targets": [language_model],
        "actions": ["ngramprint --ARPA %(dependencies)s > %(targets)s"],
    }


# -----------------------------------------------------------------------------


def do_vocab(targets):
    with open(targets[0], "w") as vocab_file:
        input_symbols = fst.Fst.read(str(intent_fst)).input_symbols()
        for i in range(input_symbols.num_symbols()):
            symbol = input_symbols.find(i).decode().strip()
            if not (symbol.startswith("__") or symbol.startswith("<")):
                print(symbol, file=vocab_file)


def task_vocab():
    """Writes all vocabulary words to a file from intent.fst."""
    return {"file_dep": [intent_fst], "targets": [vocab], "actions": [do_vocab]}


# -----------------------------------------------------------------------------


def do_dict(dictionary_paths: Iterable[Path], targets):
    with open(targets[0], "w") as dictionary_file:
        make_dict(vocab, dictionary_paths, dictionary_file, unknown_path=unknown_words)


def task_vocab_dict():
    """Creates custom pronunciation dictionary based on desired vocabulary."""
    dictionary_paths = [base_dictionary]
    if custom_words.exists():
        dictionary_paths.append(custom_words)

    return {
        "file_dep": [vocab] + dictionary_paths,
        "targets": [dictionary],
        "actions": [["rm", "-f", unknown_words], (do_dict, [dictionary_paths])],
    }


# -----------------------------------------------------------------------------


@create_after(executed="vocab_dict")
def task_vocab_g2p():
    """Guesses the pronunciations of unknown words."""
    if unknown_words.exists():
        return {
            "file_dep": [unknown_words, g2p_model],
            "targets": [guess_words],
            "actions": [
                ["rm", "-f", guess_words],
                [
                    "rhasspy-vocab_g2p",
                    "--unknown",
                    unknown_words,
                    "--model",
                    g2p_model,
                    "--nbest",
                    "5",
                    "--output",
                    guess_words,
                    "--debug",
                ],
            ],
        }


# -----------------------------------------------------------------------------


def task_kaldi_train():
    """Creates HCLG.fst for a Kaldi nnet3 or gmm model."""
    if kaldi_model_type is not None:
        return {
            "file_dep": [dictionary, language_model],
            "targets": [kaldi_graph_dir / "HCLG.fst"],
            "actions": [
                [
                    "rhasspy-kaldi-train",
                    "--kaldi-dir",
                    kaldi_dir,
                    "--model-type",
                    kaldi_model_type,
                    "--model-dir",
                    kaldi_model_dir,
                    "--dictionary",
                    dictionary,
                    "--language-model",
                    language_model,
                ]
            ],
        }


# -----------------------------------------------------------------------------

# Matches an ini header, e.g. [LightState]
intent_pattern = re.compile(r"^\[([^\]]+)\]")


def _get_intents(ini_path):
    """Yields the names of all intents in a sentences.ini file."""
    with open(ini_path, "r") as ini_file:
        for line in ini_file:
            line = line.strip()
            match = intent_pattern.match(line)
            if match:
                yield match.group(1)


# -----------------------------------------------------------------------------

DOIT_CONFIG = {"action_string_formatting": "old"}

if __name__ == "__main__":
    # Monkey patch inspect to make doit work inside Pyinstaller.
    # It grabs the line numbers of functions probably for debugging reasons, but
    # PyInstaller doesn't seem to keep that information around.
    #
    # This better thing to do would be to create a custom TaskLoader.
    import inspect

    inspect.getsourcelines = lambda obj: [0, 0]

    # Run doit main
    doit.run(globals())
