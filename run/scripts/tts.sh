#!/usr/bin/env bash
set -e
this_dir="$( cd "$( dirname "$0" )" && pwd )"

if [[ -z "${RHASSPY_DIR}" ]]; then
    echo "Missing RHASSPY_DIR environment variable"
    exit 1
fi

run_dir="$(realpath "${this_dir}/..")"
profile_dir="${run_dir}/profile"

# mqtt -> espeak -> speakers
mosquitto_sub -t 'rhasspy/intentRecognized' | \
    "${RHASSPY_DIR}/bin/jql" -r .text | \
    "${RHASSPY_DIR}/text-to-speech/espeak/run.sh" | \
    "${RHASSPY_DIR}/bin/speakers"
