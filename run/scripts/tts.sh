#!/usr/bin/env bash
this_dir="$( cd "$( dirname "$0" )" && pwd )"

# -----------------------------------------------------------------------------
# Command-line Arguments
# -----------------------------------------------------------------------------

service_dir="${this_dir}/../../text-to-speech/espeak"

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
    -q say_text 'text-to-speech.mqtt-events.say-text' '' \
    -q voice 'text-to-speech.espeak.voice' '' \
    > "${var_file}"

cat "${var_file}"
source "${var_file}"

# -----------------------------------------------------------------------------

# mqtt -> espeak -> speakers
mosquitto_sub -h "${mqtt_host}" -p "${mqtt_port}" -t "${say_text}"| \
    "${this_dir}/jql" -r '.text' | \
    "${service_dir}/run.sh" | \
    gst-launch-1.0 \
        filesrc location=/dev/stdin do-timestamp=true ! \
        rawaudioparse use-sink-caps=false format=pcm pcm-format=s16le sample-rate=16000 num-channels=1 ! \
        queue ! \
        audioconvert ! \
        audioresample ! \
        autoaudiosink
