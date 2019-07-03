#!/usr/bin/env bash
start_event='rhasspy/speech-to-text/start-listening'
stop_event='rhasspy/speech-to-text/stop-listening'
text_event='rhasspy/speech-to-text/text-captured'

nc -ukl 0.0.0.0 5000 | \
    python /main.py "$@" \
           --events-file <(mosquitto_sub -v -t "${start_event}" -t "${stop_event}") \
           --event-start "${start_event}" \
           --event-stop "${stop_event}" | \
    mosquitto_pub -l -t "${text_event}"
