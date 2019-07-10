#!/usr/bin/env bash
this_dir="$( cd "$( dirname "$0" )" && pwd )"

# -----------------------------------------------------------------------------
# Command-line Arguments
# -----------------------------------------------------------------------------

service_dir="${this_dir}/../../speech-to-text/pocketsphinx"

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
    -q acoustic_model 'speech-to-text.pocketsphinx.acoustic-model' '' \
    -q language_model 'speech-to-text.pocketsphinx.language-model' '' \
    -q dictionary 'speech-to-text.pocketsphinx.dictionary' '' \
    -q start_listening 'speech-to-text.mqtt-events.start-listening' '' \
    -q stop_listening 'speech-to-text.mqtt-events.stop-listening' '' \
    -q text_captured 'speech-to-text.mqtt-events.text-captured' '' \
    > "${var_file}"

cat "${var_file}"
source "${var_file}"

# -----------------------------------------------------------------------------

# mic -> pocketsphinx -> mqtt
gst-launch-1.0 \
    autoaudiosrc ! \
    audioconvert ! \
    audioresample ! \
    audio/x-raw, rate=16000, channels=1, format=S16LE ! \
    filesink location=/dev/stdout | \
    "${service_dir}/run.sh" \
        --debug \
        --acoustic-model "${acoustic_model}" \
        --dictionary "${dictionary}" \
        --language-model "${language_model}" \
        --events-file <(mosquitto_sub -h "${mqtt_host}" -p "${mqtt_port}" -v -t "${start_listening}" -t "${stop_listening}") \
        --event-start "${start_listening}" \
        --event-stop "${stop_listening}" | \
    mosquitto_pub -h "${mqtt_host}" -p "${mqtt_port}" -l -t "${text_captured}"
