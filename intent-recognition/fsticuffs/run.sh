#!/usr/bin/env bash
set -e
this_dir="$( cd "$( dirname "$0" )" && pwd )"
install_dir="${this_dir}"

# -----------------------------------------------------------------------------

# Load virtual environment
venv="${install_dir}/.venv"
if [[ ! -d "${venv}" ]]; then
    echo "No virtual environment found at ${venv}. Please run install.sh."
    exit 1
fi

source "${venv}/bin/activate"

# -----------------------------------------------------------------------------

export LD_LIBRARY_PATH="${venv}/lib:${LD_LIBRARY_PATH}"

python3 "${this_dir}/main.py" "$@"
