#!/usr/bin/env bash
this_dir="$( cd "$( dirname "$0" )" && pwd )"
rhasspy_dir="$(realpath "${this_dir}/../..")"

# -----------------------------------------------------------------------------
# Command-line Arguments
# -----------------------------------------------------------------------------

. "${rhasspy_dir}/etc/shflags"

DEFINE_string 'venv' "${this_dir}/.venv" 'Path to create virtual environment'
DEFINE_string 'download-dir' "${rhasspy_dir}/download" 'Directory to cache downloaded files'

DEFINE_boolean 'no-create' false 'Do not re-create the virtual environment'

FLAGS "$@" || exit $?
eval set -- "${FLAGS_ARGV}"

# -----------------------------------------------------------------------------
# Default Settings
# -----------------------------------------------------------------------------

set -e

venv="${FLAGS_venv}"
download_dir="${FLAGS_download_dir}"

if [[ "${FLAGS_no_create}" -eq "${FLAGS_TRUE}" ]]; then
    no_create='true'
fi

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

# swig
if [[ -z "$(which swig)" ]]; then
    echo "Installing swig"
    install swig
fi

# -----------------------------------------------------------------------------
# Virtual environment
# -----------------------------------------------------------------------------

if [[ -z "${no_create}" ]]; then
    # Set up fresh virtual environment
    echo "Re-creating virtual environment at ${venv}"
    rm -rf "${venv}"

    python3 -m venv "${venv}"
    source "${venv}/bin/activate"
    python3 -m pip install wheel
elif [[ -d "${venv}" ]]; then
    echo "Using virtual environment at ${venv}"
    source "${venv}/bin/activate"
fi

# -----------------------------------------------------------------------------
# Pocketsphinx for Python (no sound)
# -----------------------------------------------------------------------------

pocketsphinx_file="${download_dir}/pocketsphinx-python.tar.gz"
if [[ ! -f "${pocketsphinx_file}" ]]; then
    pocketsphinx_url='https://github.com/synesthesiam/pocketsphinx-python/releases/download/v1.0/pocketsphinx-python.tar.gz'
    echo "Downloading pocketsphinx (${pocketsphinx_url})"
    download "${pocketsphinx_url}" "${pocketsphinx_file}"
fi

python3 -m pip install "${pocketsphinx_file}"

# -----------------------------------------------------------------------------
# Python Requirements
# -----------------------------------------------------------------------------

python3 -m pip install -r "${this_dir}/requirements.txt"

# -----------------------------------------------------------------------------

echo "OK"
