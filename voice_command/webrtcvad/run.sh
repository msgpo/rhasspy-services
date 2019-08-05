#!/usr/bin/env bash
this_dir="$( cd "$( dirname "$0" )" && pwd )"
rhasspy_dir="$(realpath "${this_dir}/../..")"
venv="${this_dir}/.venv"

if [[ ! -d "${venv}" ]]; then
    echo "Virtual environment missing at ${venv}"
    echo "Did you run install.sh?"
    exit 1
fi

if [[ -z "$@" ]]; then
    echo "No command given"
    exit 1
fi

source "${venv}/bin/activate"
export PYTHONPATH="${rhasspy_dir}"

# Path to command-line parsing library
export shflags="${rhasspy_dir}/etc/shflags"

# Local path
export PATH="${this_dir}/bin:${rhasspy_dir}/bin:${PATH}"

# Run command in local venv
"$@"
