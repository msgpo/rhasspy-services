#!/usr/bin/env bash
set -e
this_dir="$( cd "$( dirname "$0" )" && pwd )"

if [[ -z "${RHASSPY_DIR}" ]]; then
    echo "Missing RHASSPY_DIR environment variable"
    exit 1
fi

run_dir="$(realpath "${this_dir}/..")"
profile_dir="${run_dir}/profile"

# mic -> pocketsphinx -> mqtt
"${RHASSPY_DIR}/bin/micsrc" | \
    "${RHASSPY_DIR}/speech-to-text/pocketsphinx/run.sh" \
        --acoustic-model "${profile_dir}/acoustic_model" \
        --dictionary "${profile_dir}/dictionary.txt" \
        --language-model "${profile_dir}/language_model.txt" \
        --events-file <(mosquitto_sub -v -t 'rhasspy/startListening' -t 'rhasspy/stopListening') \
        --event-start 'rhasspy/startListening' \
        --event-stop 'rhasspy/stopListening' | \
    mosquitto_pub -l -t 'rhasspy/textCaptured'
