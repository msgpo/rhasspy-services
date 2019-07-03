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

# Set up fresh virtual environment
venv="${install_dir}/.venv"
rm -rf "${venv}"

python3 -m venv "${venv}"
source "${venv}/bin/activate"
python3 -m pip install wheel

# -----------------------------------------------------------------------------
# jsgf2fst
# -----------------------------------------------------------------------------

jsgf2fst_file="${download_dir}/jsgf2fst-0.1.0.tar.gz"
if [[ ! -f "${jsgf2fst_file}" ]]; then
    jsgf2fst_url='https://github.com/synesthesiam/jsgf2fst/releases/download/v0.1.0/jsgf2fst-0.1.0.tar.gz'
    echo "Downloading jsgf2fst (${jsgf2fst_url})"
    curl -sSfL -o "${jsgf2fst_file}" "${jsgf2fst_url}"
fi

# -----------------------------------------------------------------------------

cd "${install_dir}" && python3 -m pip install -r "${install_dir}/requirements.txt"

# -----------------------------------------------------------------------------

echo "OK"
