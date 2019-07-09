#!/usr/bin/env bash

# -----------------------------------------------------------------------------
# Command-line Arguments
# -----------------------------------------------------------------------------

. "${HOME}/shflags"

DEFINE_string 'profile' '' 'Path to profile directory' 'p'

FLAGS "$@" || exit $?
eval set -- "${FLAGS_ARGV}"

# -----------------------------------------------------------------------------
# Default Settings
# -----------------------------------------------------------------------------

set -e

profile_dir="${FLAGS_profile}"

clients=()

# -----------------------------------------------------------------------------
# Profile
# -----------------------------------------------------------------------------

if [[ ! -z "${profile_dir}" ]]; then
    profile_yml="${profile_dir}/profile.yml"

    var_file="$(mktemp)"
    function finish {
        rm -f "${var_file}"
    }

    trap finish EXIT

    export profile_dir
    yq "${profile_yml}" \
       -q clients 'audio-input.pulseaudio.clients' '' \
       > "${var_file}"

    source "${var_file}"
fi

# -----------------------------------------------------------------------------

clients+=("$@")
if [[ -z "${clients[@]}" ]]; then
    echo "At least one client is required."
    exit 1
fi

export clients
client_str="$(echo "${clients[@]}" | sed -e 's/ /,/g')"

echo "Sending audio to ${client_str}"

gst-launch-1.0 \
    pulsesrc ! \
    audioconvert ! \
    audioresample ! \
    audio/x-raw, rate=16000, channels=1, format=S16LE ! \
    multiudpsink clients="${client_str}"
