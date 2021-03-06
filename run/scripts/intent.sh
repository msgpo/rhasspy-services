#!/usr/bin/env bash
this_dir="$( cd "$( dirname "$0" )" && pwd )"

# -----------------------------------------------------------------------------
# Command-line Arguments
# -----------------------------------------------------------------------------

service_dir="${this_dir}/../../intent-recognition/fsticuffs"

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
    -q intent_fst 'intent-recognition.fsticuffs.intent-fst' '' \
    -q recognize_intent 'intent-recognition.mqtt-events.recognize-intent' '' \
    -q intent_recognized 'intent-recognition.mqtt-events.intent-recognized' '' \
    > "${var_file}"

cat "${var_file}"
source "${var_file}"

# -----------------------------------------------------------------------------

# mqtt -> fsticuffs -> mqtt
mosquitto_sub -h "${mqtt_host}" -p "${mqtt_port}" -t "${recognize_intent}" | \
    "${service_dir}/run.sh" \
        --debug \
        --intent-fst "${intent_fst}" \
        --skip-unknown | \
    mosquitto_pub -h "${mqtt_host}" -p "${mqtt_port}" -l -t "${intent_recognized}"
