#!/usr/bin/env bash
set -e
this_dir="$( cd "$( dirname "$0" )" && pwd )"
rhasspy_dir="$(realpath "${this_dir}/../../..")"
lang_dir="${rhasspy_dir}/languages/english/en-us_pocketsphinx-cmu"
raw_file="${this_dir}/turn_on_living_room_lamp.raw"

cat "${raw_file}" | \
    rhasspy-pocketsphinx \
        --acoustic-model "${lang_dir}/acoustic_model" \
        --dictionary "${lang_dir}/base_dictionary.txt" \
        --language-model "${lang_dir}/base_language_model.txt" \
        --debug
