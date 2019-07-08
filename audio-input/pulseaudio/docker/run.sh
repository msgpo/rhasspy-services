#!/usr/bin/env bash
program_name="$(basename "$0")"

if [[ -z "$2" ]]; then
    echo "Usage: ${program_name} HOST PORT [PORT]"
    exit 1
fi

host="$1"
port="$2"

gst-launch-1.0 \
    pulsesrc ! \
    audioconvert ! \
    audioresample ! \
    audio/x-raw, rate=16000, channels=1, format=S16LE ! \
    udpsink host="${host}" port="${port}"
