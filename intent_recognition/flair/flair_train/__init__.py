#!/usr/bin/env python3
import os
import random
import logging
import shutil
import subprocess
import concurrent.futures
import time
import math
from collections import defaultdict
from typing import List, Dict, Optional, Any

import pywrapfst as fst
from jsgf2fst import fstprintall, symbols2intent

from flair.data import Sentence, Token
from flair.models import SequenceTagger, TextClassifier
from flair.embeddings import FlairEmbeddings, StackedEmbeddings, DocumentRNNEmbeddings
from flair.data import TaggedCorpus
from flair.trainers import ModelTrainer

# Configure logging (flair screws with it)
import logging.config

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
            "rhasspy": {"handlers": ["rhasspy.handler"], "propagate": False},
            "flair": {
                "handlers": ["rhasspy.handler"],
                "level": "INFO",
                "propagate": False,
            },
        },
        "root": {"handlers": ["rhasspy.handler"]},
    }
)

logger = logging.getLogger("flair_rhasspy")

# -----------------------------------------------------------------------------


def fsts_to_flair(
    intent_fst: fst.Fst,
    embeddings: List[str],
    cache_dir: str,
    data_dir: str,
    samples: Optional[int] = None,
    max_epochs: int = 100,
):
    assert len(embeddings) > 0, "No word embeddings"

    if os.path.exists(data_dir):
        shutil.rmtree(data_dir)

    # Create directories to write training data to
    class_data_dir = os.path.join(data_dir, "classification")
    ner_data_dir = os.path.join(data_dir, "ner")
    os.makedirs(class_data_dir, exist_ok=True)
    os.makedirs(ner_data_dir, exist_ok=True)

    # Convert FST to training data
    # { intent: [ { 'text': ..., 'entities': { ... } }, ... ] }
    sentences_by_intent: Dict[str, Any] = {}

    # Get sentences for training
    start_time = time.time()

    if samples is not None:
        # Generate samples
        num_intents = sum(1 for a in intent_fst.arcs(intent_fst.start()))
        logger.debug(
            f"Generating {samples} sample(s) from {num_intents} intent(s)"
        )

        sentences_by_intent = sample_sentences_by_intent(intent_fst, samples)
    else:
        # Exhaustively generate all sentences
        logger.debug("Generating all possible sentences (may take a long time)")
        sentences_by_intent = make_sentences_by_intent(intent_fst)

    sentence_time = time.time() - start_time
    logger.debug(f"Generated sentences in {sentence_time} second(s)")

    # Get least common multiple in order to balance sentences by intent
    lcm_sentences = lcm(*(len(sents) for sents in sentences_by_intent.values()))

    # Generate examples
    class_sentences = []
    ner_sentences = defaultdict(list)
    for intent_name, intent_sents in sentences_by_intent.items():
        num_repeats = max(1, lcm_sentences // len(intent_sents))
        for intent_sent in intent_sents:
            # Only train an intent classifier if there's more than one intent
            if len(sentences_by_intent) > 1:
                # Add balanced copies
                for i in range(num_repeats):
                    class_sent = Sentence(labels=[intent_name])
                    for word in intent_sent["tokens"]:
                        class_sent.add_token(Token(word))

                    class_sentences.append(class_sent)

            if len(intent_sent["entities"]) == 0:
                continue  # no entities, no sequence tagger

            # Named entity recognition (NER) example
            token_idx = 0
            entity_start = {ev["start"]: ev for ev in intent_sent["entities"]}
            entity_end = {ev["end"]: ev for ev in intent_sent["entities"]}
            entity = None

            word_tags = []
            for word in intent_sent["tokens"]:
                # Determine tag label
                tag = "O" if not entity else f"I-{entity}"
                if token_idx in entity_start:
                    entity = entity_start[token_idx]["entity"]
                    tag = f"B-{entity}"

                word_tags.append((word, tag))

                # word ner
                token_idx += len(word) + 1

                if (token_idx - 1) in entity_end:
                    entity = None

            # Add balanced copies
            for i in range(num_repeats):
                ner_sent = Sentence()
                for word, tag in word_tags:
                    token = Token(word)
                    token.add_tag("ner", tag)
                    ner_sent.add_token(token)

                ner_sentences[intent_name].append(ner_sent)

    # --------------
    # Start training
    # --------------

    # Load word embeddings
    logger.debug(f"Loading word embeddings from {cache_dir}")
    word_embeddings = [
        FlairEmbeddings(os.path.join(cache_dir, "embeddings", e)) for e in embeddings
    ]

    if len(class_sentences) > 0:
        logger.debug("Training intent classifier")

        # Random 80/10/10 split
        class_train, class_dev, class_test = split_data(class_sentences)
        class_corpus = TaggedCorpus(class_train, class_dev, class_test)

        # Intent classification
        doc_embeddings = DocumentRNNEmbeddings(
            word_embeddings,
            hidden_size=512,
            reproject_words=True,
            reproject_words_dimension=256,
        )

        classifier = TextClassifier(
            doc_embeddings,
            label_dictionary=class_corpus.make_label_dictionary(),
            multi_label=False,
        )

        logger.debug(f"Intent classifier has {len(class_sentences)} example(s)")
        trainer = ModelTrainer(classifier, class_corpus)
        trainer.train(class_data_dir, max_epochs=max_epochs)
    else:
        logger.info("Skipping intent classifier training")

    if len(ner_sentences) > 0:
        logger.debug(f"Training {len(ner_sentences)} NER sequence tagger(s)")

        # Named entity recognition
        stacked_embeddings = StackedEmbeddings(word_embeddings)

        for intent_name, intent_ner_sents in ner_sentences.items():
            ner_train, ner_dev, ner_test = split_data(intent_ner_sents)
            ner_corpus = TaggedCorpus(ner_train, ner_dev, ner_test)

            tagger = SequenceTagger(
                hidden_size=256,
                embeddings=stacked_embeddings,
                tag_dictionary=ner_corpus.make_tag_dictionary(tag_type="ner"),
                tag_type="ner",
                use_crf=True,
            )

            ner_intent_dir = os.path.join(ner_data_dir, intent_name)
            os.makedirs(ner_intent_dir, exist_ok=True)

            logger.debug(
                f"NER tagger for {intent_name} has {len(intent_ner_sents)} example(s)"
            )
            trainer = ModelTrainer(tagger, ner_corpus)
            trainer.train(ner_intent_dir, max_epochs=max_epochs)
    else:
        logger.info("Skipping NER sequence tagger training")


# -----------------------------------------------------------------------------


def sample_sentences_by_intent(
    intent_fst: fst.Fst, num_samples: int
) -> Dict[str, Any]:
    def sample_sentences(intent_name: str, sample_fst: fst.Fst):
        rand_fst = fst.randgen(sample_fst, npath=num_samples)

        sentences: List[Dict[str, Any]] = []
        for symbols in fstprintall(rand_fst, exclude_meta=False):
            intent = symbols2intent(symbols)
            intent_name = intent["intent"]["name"]
            sentences.append(intent)

        return sentences

    # Generate samples in parallel
    future_to_intent = {}
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for intent_arc in intent_fst.arcs(intent_fst.start()):
            # Strip __label__ from front of output symbol
            intent_name = intent_fst.output_symbols().find(intent_arc.olabel).decode()[9:]

            # Create copy of FST, starting at this intent's state
            sample_fst = intent_fst.copy()
            sample_fst.set_start(intent_arc.nextstate)

            # Generate sample sentences for this intent
            future = executor.submit(sample_sentences, intent_name, sample_fst)
            future_to_intent[future] = intent_name

    # { intent: [ { 'text': ..., 'entities': { ... } }, ... ] }
    sentences_by_intent: Dict[str, Any] = {}
    for future, intent_name in future_to_intent.items():
        sentences_by_intent[intent_name] = future.result()

    return sentences_by_intent


# -----------------------------------------------------------------------------


def split_data(data, split=0.1):
    """Randomly splits a data set into train, dev, and test sets"""

    random.shuffle(data)
    split_index = int(len(data) * split)

    # 1 - (2*split)
    train = data[(split_index * 2) :]

    # split
    dev = data[:split_index]

    # split
    test = data[split_index : (split_index * 2)]

    return train, dev, test


# -----------------------------------------------------------------------------


def make_sentences_by_intent(intent_fst: fst.Fst) -> Dict[str, Any]:
    # { intent: [ { 'text': ..., 'entities': { ... } }, ... ] }
    sentences_by_intent: Dict[str, Any] = defaultdict(list)

    for symbols in fstprintall(intent_fst, exclude_meta=False):
        intent = symbols2intent(symbols)
        intent_name = intent["intent"]["name"]
        sentences_by_intent[intent_name].append(intent)

    return sentences_by_intent


# -----------------------------------------------------------------------------


def lcm(*nums: int) -> int:
    """Returns the least common multiple of the given integers"""
    if len(nums) == 0:
        return 1

    nums_lcm = nums[0]
    for n in nums[1:]:
        nums_lcm = (nums_lcm * n) // math.gcd(nums_lcm, n)

    return nums_lcm
