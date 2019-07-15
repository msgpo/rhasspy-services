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

function python_module {
    python3 -c "import $1" 2>/dev/null
    if [[ "$?" -eq "0" ]]; then
        echo "$1"
    fi
}

export -f python_module

# python 3
if [[ -z "$(which python3)" ]]; then
    echo "Installing python 3"
    install python3
fi

# pip
if [[ -z "$(python_module pip)" ]]; then
    echo "Installing python pip"
    install python3-pip
fi

# venv
if [[ -z "$(python_module venv)" ]]; then
    echo "Installing python venv"
    install python3-venv
fi

# sox
if [[ -z "$(which sox)" ]]; then
    echo "Installing sox"
    install sox
fi

# espeak
if [[ -z "$(which espeak)" ]]; then
    echo "Installing espeak"
    install espeak
fi

# Set up fresh virtual environment
venv="${install_dir}/.venv"
rm -rf "${venv}"

python3 -m venv "${venv}"
source "${venv}/bin/activate"
python3 -m pip install wheel

# -----------------------------------------------------------------------------

cd "${install_dir}" && \
    python3 -m pip install \
            -r "${install_dir}/requirements.txt"

# -----------------------------------------------------------------------------

echo "OK"
