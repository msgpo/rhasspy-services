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

# python 3
if [[ -z "$(which python3)" ]]; then
    echo "Installing python 3"
    install python3
fi

# phonetisaurus
if [[ -z "$(which phonetisaurus-apply)" ]]; then
    echo "Installing phonetisaurus"
    install libfst-dev
    cd "${this_dir}" && \
        tar -xf phonetisaurus-2019.tar.gz && cd phonetisaurus/ && \
        ./configure --prefix="${this_dir}" && \
        make -j 4 && \
        make install && \
        rm -rf phoneitsaurus/
fi

# -----------------------------------------------------------------------------

cd "${install_dir}" && python3 -m pip install -r "${install_dir}/requirements.txt"

# -----------------------------------------------------------------------------

echo "OK"
