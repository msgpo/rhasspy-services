#!/usr/bin/env bash
set -e
this_dir="$( cd "$( dirname "$0" )" && pwd )"

# -----------------------------------------------------------------------------

temp_list="$(mktemp)"
function finish {
    rm -f "${temp_list}"
}

trap finish EXIT

# -----------------------------------------------------------------------------

guess_event='rhasspy/grapheme-to-phoneme/guess-pronunciations'
pron_event='rhasspy/grapheme-to-phoneme/pronunciations'

mosquitto_sub -t "${guess_event}" | while read -r line;
do
    echo -n "${line}" | jq -r .[]  > "${temp_list}"
    phonetisaurus-apply --word_list "${temp_list}" "$@" | \
        python /main.py |
        mosquitto_pub -l -t "${pron_event}"
done
