#!/usr/bin/env bash
set -e
this_dir="$( cd "$( dirname "$0" )" && pwd )"

if [[ ! -z "$1" ]]; then
    this_dir="$1"
fi

install_dir="${this_dir}"
download_dir="${install_dir}/download"
mkdir -p "${download_dir}"

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

# python3-dev
if [[ -z "$(python_module distutils.sysconfig)" ]]; then
    echo "Installing python dev"
    install python3-dev
fi

# build-essential
if [[ -z "$(which g++)" ]]; then
    echo "Installing build tools"
    install build-essential
fi

# swig
if [[ -z "$(which swig)" ]]; then
    echo "Installing swig"
    install swig
fi

# Set up fresh virtual environment
venv="${install_dir}/.venv"
rm -rf "${venv}"

python3 -m venv "${venv}"
source "${venv}/bin/activate"
python3 -m pip install wheel

# -----------------------------------------------------------------------------
# Pocketsphinx for Python (no sound)
# -----------------------------------------------------------------------------

pocketsphinx_file="${download_dir}/pocketsphinx-python.tar.gz"
if [[ ! -f "${pocketsphinx_file}" ]]; then
    pocketsphinx_url='https://github.com/synesthesiam/pocketsphinx-python/releases/download/v1.0/pocketsphinx-python.tar.gz'
    echo "Downloading pocketsphinx (${pocketsphinx_url})"
    wget -q -O "${pocketsphinx_file}" "${pocketsphinx_url}"
fi

# -----------------------------------------------------------------------------

cd "${install_dir}" && python3 -m pip install -r "${install_dir}/requirements.txt"

# -----------------------------------------------------------------------------

echo "OK"
