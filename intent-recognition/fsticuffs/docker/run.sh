#!/usr/bin/env bash
recognize_event='rhasspy/intent-recognition/recognize-intent'
recognized_event='rhasspy/intent-recognition/intent-recognized'

mosquitto_sub -t "${recognize_event}" | jql -r .text | \
    python /main.py "$@" | \
    mosquitto_pub -l -t "${recognized_event}"
