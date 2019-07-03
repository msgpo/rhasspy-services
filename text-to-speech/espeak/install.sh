#!/usr/bin/env bash
set -e
this_dir="$( cd "$( dirname "$0" )" && pwd )"

if [[ ! -z "$1" ]]; then
    this_dir="$1"
fi

install_dir="${this_dir}"

# -----------------------------------------------------------------------------
# Debian dependencies
# -----------------------------------------------------------------------------

function install {
    sudo apt-get install -y "$@"
}

# espeak
if [[ -z "$(which espeak)" ]]; then
    echo "Installing espeak"
    install espeak
fi

# -----------------------------------------------------------------------------

echo "OK"
