#!/usr/bin/env python3
import os
import re
import argparse
from pathlib import Path

import yaml
import pydash
import doit
from doit import create_after

# -----------------------------------------------------------------------------


def env_constructor(loader, node):
    """Expands !env STRING to replace environment variables in STRING."""
    return os.path.expandvars(node.value)


yaml.SafeLoader.add_constructor("!env", env_constructor)

# -----------------------------------------------------------------------------

# Profile directory
profile_dir = Path(os.getenv("profile_dir", os.getcwd()))
os.environ["profile_dir"] = str(profile_dir)


# Load profile
profile_yaml = profile_dir / "profile.yml"

with open(profile_yaml, "r") as profile_file:
    profile = yaml.safe_load(profile_file)


# Get default values
def ppath(query: str, default: str) -> Path:
    return Path(pydash.get(profile, query, profile_dir / Path(default)))


# Inputs
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


def task_grammars():
    """Transforms sentences.ini into JSGF grammars, one per intent."""
    return {
        "file_dep": [sentences_ini],
        "targets": [
            grammar_dir / f"{intent}.gram" for intent in _get_intents("sentences.ini")
        ],
        "actions": [
            [
                "rhasspy-ini_jsgf",
                "--ini-file",
                sentences_ini,
                "--grammar-dir",
                grammar_dir,
                "--debug",
            ]
        ],
    }


@create_after(executed="grammars")
def task_fst_arpa():
    """Transforms intent JSGF grammars into single intent.fst and ARPA language model."""
    intents = list(_get_intents("sentences.ini"))
    return {
        "file_dep": [grammar_dir / f"{intent}.gram" for intent in intents]
        + list(slots_dir.glob("*")),
        "targets": [fsts_dir / f"{intent}.fst" for intent in intents]
        + [intent_fst, vocab, language_model],
        "actions": [
            [
                "rhasspy-jsgf_fst_arpa",
                "--grammar-dir",
                grammar_dir,
                "--fst-dir",
                fsts_dir,
                "--fst",
                intent_fst,
                "--vocab",
                vocab,
                "--arpa",
                language_model,
                "--slots-dir",
                slots_dir,
                "--debug",
            ]
        ],
    }


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

if __name__ == "__main__":
    doit.run(globals())
