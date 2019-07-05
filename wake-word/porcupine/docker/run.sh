#!/usr/bin/env bash
start_event='rhasspy/wake-word/start-listening'
stop_event='rhasspy/wake-word/stop-listening'
wake_event='rhasspy/wake-word/detected'

nc -ukl 0.0.0.0 5000 | \
    python /main.py "$@" \
           --library /porcupine/lib/x86_64/libpv_porcupine.so \
           --model /porcupine/lib/common/porcupine_params.pv \
           --keyword /porcupine/resources/keyword_files/linux/porcupine_linux.ppn \
           --events-file <(mosquitto_sub -v -t "${start_event}" -t "${stop_event}") \
           --event-start "${start_event}" \
           --event-stop "${stop_event}" | \
    mosquitto_pub -l -t "${wake_event}"
