#!/usr/bin/env python3
import os
import re
import sys
import argparse
import logging
from pathlib import Path
from typing import Dict, Set
from collections import deque

import yaml
import pydash
import pywrapfst as fst
import doit
from doit import create_after

from jsgf2fst.jsgf2fst import (
    get_parser,
    grammar_dependencies,
    grammar_to_fsts,
    slot_to_grammar,
    make_intent_fst,
)

from training.ini_jsgf import make_grammars

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

# Shared symbol tables
eps = "<eps>"

input_symbols = fst.SymbolTable()
input_symbols.add_symbol(eps)

output_symbols = fst.SymbolTable()
output_symbols.add_symbol(eps)

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


def make_slot_fst(slot_grammar: str, targets):
    grammar_name, slot_fsts = grammar_to_fsts(
        slot_grammar,
        input_symbols=input_symbols,
        output_symbols=output_symbols,
        eps=eps,
    )

    main_rule = grammar_name + "." + grammar_name
    slot_fst = slot_fsts[main_rule]

    slot_fst.write(targets[0])


def make_grammar_fsts(grammar_path: Path, replace_fsts: Dict[str, Path], targets):
    grammar = grammar_path.read_text()
    grammar_name, grammar_fsts = grammar_to_fsts(
        grammar, input_symbols=input_symbols, output_symbols=output_symbols, eps=eps
    )

    main_rule = grammar_name + "." + grammar_name

    for replace_name, fst_path in replace_fsts.items():
        replace_fst = fst.Fst.read(str(fst_path))

        for i in range(input_symbols.num_symbols()):
            s1 = input_symbols.find(i).decode()
            s2 = replace_fst.input_symbols().find(i).decode()
            assert s1 == s2, (i, s1, s2)

        replace_symbol = "__replace__" + replace_name
        replace_idx = input_symbols.find(replace_symbol)
        if replace_idx >= 0:
            grammar_fsts[main_rule] = fst.replace(
                [(-1, grammar_fsts[main_rule]), (replace_idx, replace_fst)],
                epsilon_on_replace=True,
            )

    for rule_name, rule_fst in grammar_fsts.items():
        fst_path = fsts_dir / f"{rule_name}.fst"
        rule_fst.write(str(fst_path))

        if rule_name == main_rule:
            grammar_fst_path = fsts_dir / f"{grammar_name}.fst"
            grammar_fst.write(str(grammar_fst_path))


# -----------------------------------------------------------------------------


@create_after(executed="grammars")
def task_grammar_fsts():
    """Creates grammar FSTs from JSGF grammars and relevant slots."""
    tasks = []
    used_slots: Set[str] = set()
    input_words: Set[str] = set()
    output_words: Set[str] = set()

    for intent in intents:
        grammar_path = grammar_dir / f"{intent}.gram"
        grammar = grammar_path.read_text()
        grammar_deps = grammar_dependencies(grammar)

        rule_names = []

        # Add vocabulary to shared symbol tables
        input_words.update(grammar_deps.input_words)
        output_words.update(grammar_deps.output_words)

        # Process dependencies
        replace_fsts: Dict[str, Path] = {}
        for node, data in grammar_deps.graph.nodes(data=True):
            if data["type"] == "slot":
                slot_name = node
                if slot_name in used_slots:
                    continue

                slot_path = slots_dir / slot_name
                slot_grammar = slot_to_grammar(slots_dir, slot_name)
                slot_grammar_deps = grammar_dependencies(slot_grammar)

                # Add vocabulary to shared symbol tables
                input_words.update(slot_grammar_deps.input_words)
                output_words.update(slot_grammar_deps.output_words)

                # JSGF -> FST
                slot_fst_path = fsts_dir / f"{slot_name}.slot.fst"
                tasks.append(
                    {
                        "name": slot_name + "_fst",
                        "file_dep": [slot_path],
                        "targets": [slot_fst_path],
                        "actions": [(make_slot_fst, [slot_grammar])],
                    }
                )

                replace_fsts["$" + slot_name] = slot_fst_path

            elif (data["type"] == "grammar") and (node != intent):
                # Grammar dependency
                sub_grammar_name = node
                sub_rule = sub_grammar_name + "." + sub_grammar_name
                sub_fst_path = fsts_dir / f"{sub_rule}.fst"
                replace_fsts[sub_rule] = sub_fst_path
            elif data["type"] == "rule":
                # Rule dependency
                rule_names.append(node)
            elif data["type"] == "reference":
                rule_name = node
                rule_grammar = rule_name.split(".", maxsplit=1)[0]
                if rule_grammar != intent:
                    # Rule dependency from other grammar
                    replace_fsts[rule_name] = fsts_dir / f"{rule_name}.fst"

        # All rule/grammar FSTs that will be generated
        grammar_fst_paths = [fsts_dir / f"{rule_name}.fst" for rule_name in rule_names]
        grammar_fst_paths.append(fsts_dir / f"{intent}.fst")

        tasks.append(
            {
                "name": intent + "_fst",
                "file_dep": [grammar_path] + list(replace_fsts.values()),
                "targets": grammar_fst_paths,
                "actions": [(make_grammar_fsts, [grammar_path, replace_fsts])],
            }
        )

    # Construct shared symbol tables
    for word in sorted(input_words):
        input_symbols.add_symbol(word)

    for word in sorted(output_words):
        output_symbols.add_symbol(word)

    # Start tasks *after* symbol tables have been generated
    for task in tasks:
        yield task


# -----------------------------------------------------------------------------


@create_after(executed="grammars")
def task_intent_fst():
    """Merges grammar FSTs into single intent.fst."""
    fst_paths = {intent: fsts_dir / f"{intent}.fst" for intent in intents}
    return {
        "file_dep": list(fst_paths.values()),
        "targets": [intent_fst],
        "actions": [
            (
                lambda targets: make_intent_fst(
                    {
                        intent: fst.Fst.read(str(fst_paths[intent]))
                        for intent in intents
                    },
                    input_symbols,
                    output_symbols,
                    eps=eps,
                ).write(targets[0])
            )
        ],
    }


# -----------------------------------------------------------------------------


def task_language_model():
    """Creates an ARPA language model from intent.fst."""
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

    # model -> ARPA
    yield {
        "name": "intent_arpa",
        "file_dep": [intent_model],
        "targets": [language_model],
        "actions": ["ngramprint --ARPA %(dependencies)s > %(targets)s"],
    }


# -----------------------------------------------------------------------------


def task_vocab():
    """Writes all vocabulary words to a file from intent.fst."""
    def make_vocab(targets):
        with open(targets[0], "w") as vocab_file:
            input_symbols = fst.Fst.read(str(intent_fst)).input_symbols()
            for i in range(input_symbols.num_symbols()):
                symbol = input_symbols.find(i).decode().strip()
                if not (symbol.startswith("__") or symbol.startswith("<")):
                    print(symbol, file=vocab_file)

    return {"file_dep": [intent_fst], "targets": [vocab], "actions": [make_vocab]}


# -----------------------------------------------------------------------------


def task_vocab_dict():
    """Creates custom pronunciation dictionary based on desired vocabulary."""
    extra_deps = []
    extra_args = []
    if custom_words.exists():
        extra_deps.append(custom_words)
        extra_args.extend(["--dictionary", custom_words])

    return {
        "file_dep": [vocab, base_dictionary] + extra_deps,
        "targets": [dictionary],
        "actions": [
            ["rm", "-f", unknown_words],
            [
                "rhasspy-vocab_dict",
                "--vocab",
                vocab,
                "--dictionary",
                base_dictionary,
                "--unknown",
                unknown_words,
                "--output",
                dictionary,
                " --debug",
            ]
            + extra_args,
        ],
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
    if kaldi_model_type:
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
