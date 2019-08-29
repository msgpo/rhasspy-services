#!/usr/bin/env bash
set -e

# Directory of *this* script
this_dir="$( cd "$( dirname "$0" )" && pwd )"
rhasspy_dir="$(realpath "${this_dir}/../..")"

venv="${rhasspy_dir}/.venv"
if [[ ! -d "${venv}" ]]; then
    echo "Missing virtual environment at ${venv}"
    exit 1;
fi

cd "${this_dir}"
source "${rhasspy_dir}/.venv/bin/activate"
export LD_LIBRARY_PATH="${venv}/lib"

python3 test.py "$@"
