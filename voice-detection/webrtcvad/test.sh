#!/usr/bin/env bash
set -e
this_dir="$( cd "$( dirname "$0" )" && pwd )"
install_dir="${this_dir}"

wav_file="${install_dir}/test/turn_on_living_room_lamp.wav"

gst-launch-1.0 filesrc location="${wav_file}" ! \
                wavparse ! \
                audioconvert ! \
                audioresample ! \
                audio/x-raw, rate=16000, channels=1, format=S16LE ! \
                filesink location=/dev/stdout | \
    "${install_dir}/run.sh"
