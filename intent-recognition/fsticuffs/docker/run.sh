#!/usr/bin/env bash
text_event='rhasspy/speech-to-text/text-captured'
recognized_event='rhasspy/intent-recognition/intent-recognized'

mosquitto_sub -t "${text_event}" | \
    python /main.py "$@" | \
    mosquitto_pub -l -t "${recognized_event}"
