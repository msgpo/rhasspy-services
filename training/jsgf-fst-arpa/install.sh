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

# openfst
if [[ -z "$(which fstminimize)" ]]; then
    echo "Installing openfst"
    install libfst-tools
fi

# sphinxbase-utils
if [[ -z "$(which sphinx_jsgf2fsg)" ]]; then
    echo "Installing sphinxbase-utils"
    install sphinxbase-utils
fi

# opengrm
if [[ -z "$(which ngrammake)" ]]; then
    echo "Installing opengrm"
    install libfst-dev
    cd "${this_dir}" && \
        tar -xf download/opengrm-ngram-1.3.4.tar.gz && \
        cd opengrm-ngram-1.3.4/ && \
        ./configure --prefix="${this_dir}" && \
        make -j 4 && \
        make install && \
        rm -rf /opengrm-ngram-1.3.4/
fi

# Set up fresh virtual environment
venv="${install_dir}/.venv"
rm -rf "${venv}"

python3 -m venv "${venv}"
source "${venv}/bin/activate"
python3 -m pip install wheel

# -----------------------------------------------------------------------------

cd "${install_dir}" && python3 -m pip install -r "${install_dir}/requirements.txt"

# -----------------------------------------------------------------------------

echo "OK"
