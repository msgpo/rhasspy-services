#!/usr/bin/env bash
set -e
this_dir="$( cd "$( dirname "$0" )" && pwd )"
raw_file="${this_dir}/test/turn_on_living_room_lamp.raw"

cat "${raw_file}" | webrtcvad
