#!/usr/bin/env bash
set -e

# -----------------------------------------------------------------------------

while read line
do
    espeak --stdout "$@" "${line}" | sox -t wav - -t raw -r 16000 -e signed-integer -c 1 -
done
