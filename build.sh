#!/usr/bin/env bash
this_dir="$( cd "$( dirname "$0" )" && pwd )"
venv="${this_dir}/.venv"

if [[ ! -d "${venv}" ]]; then
    echo "Virtual environment missing at ${venv}"
    echo "Did you run install.sh?"
    exit 1
fi

if [[ -z "$1" ]]; then
    echo "No spec file given"
    exit 1
fi

source "${venv}/bin/activate"
export LD_LIBRARY_PATH="${venv}/lib:${LD_LIBRARY_PATH}"

# Run command in Rhasspy venv
pyinstaller -y "$1"
