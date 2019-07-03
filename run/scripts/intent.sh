#!/usr/bin/env bash
set -e
this_dir="$( cd "$( dirname "$0" )" && pwd )"

if [[ -z "${RHASSPY_DIR}" ]]; then
    echo "Missing RHASSPY_DIR environment variable"
    exit 1
fi

run_dir="$(realpath "${this_dir}/..")"
profile_dir="${run_dir}/profile"

# mqtt -> fsticuffs -> mqtt
mosquitto_sub -t 'rhasspy/textCaptured' | \
    "${RHASSPY_DIR}/bin/jql" -r .text | \
    "${RHASSPY_DIR}/intent-recognition/fsticuffs/run.sh" \
        --intent-fst "${profile_dir}/intent.fst" \
        --skip-unknown | \
    mosquitto_pub -l -t 'rhasspy/intentRecognized'
