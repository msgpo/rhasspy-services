#!/usr/bin/env bash
set -e

start_training='rhasspy/training/start-training'
training_complete='rhasspy/training/training-complete'

mosquitto_sub -v -t "${start_training}" | while read -r line;
do
    echo "Training started"

    # ini -> jsgf
    python /ini-jsgf.py \
           --grammar-dir /grammars \
           < /profile/sentences.ini

    # jsgf -> fst, arpa
    python /jsgf-fst-arpa.py \
           --grammar-dir /grammars \
           --fst /profile/intent.fst \
           --arpa /profile/language_model.txt \
           --vocab /profile/vocab.txt

    # vocab -> dict
    python /vocab-dict.py \
           --vocab /profile/vocab.txt \
           --dictionary /profile/base_dictionary.txt \
           > /profile/dictionary.txt

    echo "Training complete"
    mosquitto_pub -t "${training_complete}" -m '{}'
done
