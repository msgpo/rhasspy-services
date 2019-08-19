#!/usr/bin/env bash
set -e

export this_dir="$( cd "$( dirname "$0" )" && pwd )"

if [[ -z "${rhasspy_dir}" ]]; then
    export rhasspy_dir='/usr/lib/rhasspy'
fi

export profile_dir="${this_dir}/profile"

# -----------------------------------------------------------------------------

rhasspy-train \
    --profile "${profile_dir}" \
    --debug

unknown_words="${profile_dir}/unknown.txt"
guess_words="${profile_dir}/guess_words.json"
if [[ -f "${unknown_words}" ]]; then
    echo "Exiting because of unknown words:"
    cat "${unknown_words}"
    echo ''
    echo "Add correct pronunciation(s) to profile/custom_words.txt"
    jq . < "${guess_words}"
    exit 1
fi

# -----------------------------------------------------------------------------

supervisord -c "${this_dir}/supervisord.conf"
