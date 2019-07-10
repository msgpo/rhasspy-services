#!/usr/bin/env bash
this_dir="$( cd "$( dirname "$0" )" && pwd )"

# -----------------------------------------------------------------------------
# Command-line Arguments
# -----------------------------------------------------------------------------

. "${this_dir}/shflags"

DEFINE_string 'profile' '' 'Path to profile directory' 'p'

FLAGS "$@" || exit $?
eval set -- "${FLAGS_ARGV}"

if [[ -z "${FLAGS_profile}" ]]; then
    echo 'Profile directory is required'
    exit 1
fi

profile_dir="$(realpath "${FLAGS_profile}")"

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
    -q play_uri 'audio-output.mqtt-events.play-uri' '' \
    -q uri_played 'audio-output.mqtt-events.uri-played' '' \
    > "${var_file}"

cat "${var_file}"
source "${var_file}"

# -----------------------------------------------------------------------------

# mqtt -> speakers
mosquitto_sub -h "${mqtt_host}" -p "${mqtt_port}" -v -t "${play_uri}/#" | \
    while read -r topic uri;
    do
        echo "${uri}"
        gst-launch-1.0 \
            uridecodebin uri="${uri}" ! \
            pulsesink

        request_id="$(echo "${topic}" | sed -e "s|^${play_uri}||")"
        echo "${request_id}"

        mosquitto_pub -h "${mqtt_host}" -p "${mqtt_port}" -t "${uri_played}${request_id}" -m '{}'
    done
