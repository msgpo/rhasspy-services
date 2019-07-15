#!/usr/bin/env python3
import logging

logger = logging.getLogger("pocketsphinx_rhasspy")

import os
import sys
import jsonlines
import time
import argparse
import threading
import json
from typing import Optional, Dict, Any

import pocketsphinx

# -------------------------------------------------------------------------------------------------


def get_decoder(
    acoustic_model: str,
    dictionary: str,
    language_model: str,
    mllr_matrix: str,
    debug: bool = False,
) -> pocketsphinx.Decoder:
    """Loads the pocketsphinx decoder from command-line arguments."""
    start_time = time.time()
    decoder_config = pocketsphinx.Decoder.default_config()
    decoder_config.set_string("-hmm", acoustic_model)
    decoder_config.set_string("-dict", dictionary)
    decoder_config.set_string("-lm", language_model)

    if not debug:
        decoder_config.set_string("-logfn", os.devnull)

    if mllr_matrix and os.path.exists(mllr_matrix):
        decoder_config.set_string("-mllr", mllr_matrix)

    decoder = pocketsphinx.Decoder(decoder_config)
    end_time = time.time()

    logger.debug(f"Successfully loaded decoder in {end_time - start_time} second(s)")

    return decoder


# -------------------------------------------------------------------------------------------------


def transcribe(decoder: pocketsphinx.Decoder, audio_data: bytes) -> Dict[str, Any]:
    """Transcribes audio data to speech."""
    # Process data as an entire utterance
    start_time = time.time()
    decoder.start_utt()
    decoder.process_raw(audio_data, False, True)
    decoder.end_utt()
    end_time = time.time()

    logger.debug(f"Decoded WAV in {end_time - start_time} second(s)")

    transcription = ""
    decode_seconds = end_time - start_time
    likelihood = 0.0
    score = 0

    hyp = decoder.hyp()
    if hyp is not None:
        likelihood = decoder.get_logmath().exp(hyp.prob)
        transcription = hyp.hypstr

    result = {
        "text": transcription,
        "seconds": decode_seconds,
        "likelihood": likelihood,
        "nbest": {nb.hypstr: nb.score for nb in decoder.nbest()},
    }

    return result
