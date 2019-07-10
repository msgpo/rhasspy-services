#!/usr/bin/env bash
this_dir="$( cd "$( dirname "$0" )" && pwd )"

# -----------------------------------------------------------------------------
# Command-line Arguments
# -----------------------------------------------------------------------------

service_dir="${this_dir}/../../wake-word/porcupine"

. "${this_dir}/shflags"

DEFINE_string 'profile' '' 'Path to profile directory' 'p'
DEFINE_string 'service' "${service_dir}" 'Path to service directory'

FLAGS "$@" || exit $?
eval set -- "${FLAGS_ARGV}"

if [[ -z "${FLAGS_profile}" ]]; then
    echo 'Profile directory is required'
    exit 1
fi

profile_dir="$(realpath "${FLAGS_profile}")"
service_dir="$(realpath "${FLAGS_service}")"

export profile_dir

# -----------------------------------------------------------------------------
# Profile
# -----------------------------------------------------------------------------

set -e

var_file="$(mktemp)"
function finish {
    rm -f "${var_file}"
}

trap finish EXIT

"${this_dir}/yq" \
    "${profile_dir}/profile.yml" \
    -q mqtt_host 'mqtt.host' '' \
    -q mqtt_port 'mqtt.port' '' \
    -q library 'wake-word.porcupine.library' '' \
    -q model 'wake-word.porcupine.model' '' \
    -q keyword 'wake-word.porcupine.keyword' '' \
    -q start_listening 'wake-word.mqtt-events.start-listening' '' \
    -q stop_listening 'wake-word.mqtt-events.stop-listening' '' \
    -q detected 'wake-word.mqtt-events.detected' '' \
    > "${var_file}"

cat "${var_file}"
source "${var_file}"

# -----------------------------------------------------------------------------

# mic -> wake -> mqtt
gst-launch-1.0 \
    autoaudiosrc ! \
    audioconvert ! \
    audioresample ! \
    audio/x-raw, rate=16000, channels=1, format=S16LE ! \
    filesink location=/dev/stdout | \
    "${service_dir}/run.sh" \
        --debug \
        --auto-start \
        --library "${library}" \
        --model "${model}" \
        --keyword "${keyword}" \
        --events-file <(mosquitto_sub -h "${mqtt_host}" -p "${mqtt_port}" -v -t "${start_listening}" -t "${stop_listening}") \
        --event-start "${start_listening}" \
        --event-stop "${stop_listening}" | \
    mosquitto_pub -h "${mqtt_host}" -p "${mqtt_port}" -l -t "${detected}"
