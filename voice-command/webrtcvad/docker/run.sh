#!/usr/bin/env bash
start_event='rhasspy/voice-command/start-listening'
speech_event='rhasspy/voice-command/speech'
silence_event='rhasspy/voice-command/silence'
command_start_event='rhasspy/voice-command/command-started'
command_stop_event='rhasspy/voice-command/command-stopped'
command_timeout_event='rhasspy/voice-command/command-timeout'

nc -ukl 0.0.0.0 5001 | \
    python /main.py "$@" \
           --events-file <(mosquitto_sub -v -t "${start_event}") \
           --event-start "${start_event}" \
           --event-command-start "${command_start_event}" \
           --event-command-stop "${command_stop_event}" \
           --event-command-timeout "${command_timeout_event}" \
           --event-speech "${speech_event}" \
           --event-silence "${silence_event}" | \
    while read -r topic payload;
    do
        mosquitto_pub -t "${topic}" -m "${payload}"
    done
