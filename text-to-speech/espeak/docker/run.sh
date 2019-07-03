#!/usr/bin/env bash
set -e

host="localhost"
if [[ ! -z "$1" ]]; then
    host="$1"
fi


# -----------------------------------------------------------------------------

mosquitto_sub -h "${host}" -t 'rhasspy/text-to-speech/say-text' | \
    while read -r line;
    do
        echo "${line}"
        espeak --stdout "$@" "${line}" | \
            mosquitto_pub -h "${host}" -t 'rhasspy/audio-out/play-wav' -s
    done
