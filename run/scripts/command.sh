#!/usr/bin/env bash
this_dir="$( cd "$( dirname "$0" )" && pwd )"

# -----------------------------------------------------------------------------
# Command-line Arguments
# -----------------------------------------------------------------------------

service_dir="${this_dir}/../../voice-command/webrtcvad"

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
    -q start_listening 'voice-command.mqtt-events.start-listening' '' \
    -q speech 'voice-command.mqtt-events.speech' '' \
    -q silence 'voice-command.mqtt-events.silence' '' \
    -q command_started 'voice-command.mqtt-events.command-started' '' \
    -q command_stopped 'voice-command.mqtt-events.command-stopped' '' \
    -q command_timeout 'voice-command.mqtt-events.command-timeout' '' \
    > "${var_file}"

cat "${var_file}"
source "${var_file}"

# -----------------------------------------------------------------------------

# mic -> webrtcvad -> mqtt
gst-launch-1.0 \
    autoaudiosrc ! \
    audioconvert ! \
    audioresample ! \
    audio/x-raw, rate=16000, channels=1, format=S16LE ! \
    filesink location=/dev/stdout | \
    "${service_dir}/run.sh" \
        --debug \
        --events-file <(mosquitto_sub -h "${mqtt_host}" -p "${mqtt_port}" -v -t "${start_listening}") \
        --event-start "${start_listening}" \
        --event-command-start "${command_started}" \
        --event-command-stop "${command_stopped}" \
        --event-command-timeout "${command_timeout}" \
        --event-speech "${speech}" \
        --event-silence "${silence}" | \
    while read -r topic payload;
    do
        mosquitto_pub -h "${mqtt_host}" -p "${mqtt_port}" -t "${topic}" -m "${payload}"
    done
