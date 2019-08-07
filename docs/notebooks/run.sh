#!/usr/bin/env bash
this_dir="$( cd "$( dirname "$0" )" && pwd )"
rhasspy_dir="$(realpath "${this_dir}/../..")"
venv="${rhasspy_dir}/.venv"

if [[ ! -d "${venv}" ]]; then
    echo "Virtual environment missing at ${venv}"
    echo "Did you run install.sh?"
    exit 1
fi

source "${venv}/bin/activate"
export LD_LIBRARY_PATH="${venv}/lib:${LD_LIBRARY_PATH}"
jupyter notebook
