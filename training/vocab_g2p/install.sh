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
DEFINE_integer 'make-threads' 4 'Number of threads to use with make' 'j'

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

make_threads="${FLAGS_make_threads}"

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

function download {
    mkdir -p "$(dirname "$2")"
    curl -sSfL -o "$2" "$1"
    echo "$1 => $2"
}

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

# build tools
if [[ -z "$(which g++)" ]]; then
    echo "Installing build-essential"
    install build-essential
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
# openfst
# -----------------------------------------------------------------------------

openfst_dir="${this_dir}/openfst-1.6.9"
if [[ ! -d "${openfst_dir}/build" ]]; then
    echo "Building openfst"
    openfst_file="${download_dir}/openfst-1.6.9.tar.gz"

    if [[ ! -f "${openfst_file}" ]]; then
        openfst_url='http://openfst.org/twiki/pub/FST/FstDownload/openfst-1.6.9.tar.gz'
        echo "Downloading openfst (${openfst_url})"
        download "${openfst_url}" "${openfst_file}"
    fi

    cd "${this_dir}" && \
        tar -xf "${openfst_file}" && \
        cd "${openfst_dir}" && \
        ./configure "--prefix=${openfst_dir}/build" --enable-far --enable-static --enable-shared --enable-ngram-fsts && \
        make -j "${make_threads}" && \
        make install
fi

cp -R "${openfst_dir}"/build/bin/* "${venv}/bin/"
cp -R "${openfst_dir}"/build/include/* "${venv}/include/"
cp -R "${openfst_dir}"/build/lib/*.so* "${venv}/lib/"

# -----------------------------------------------------------------------------
# phonetisaurus
# -----------------------------------------------------------------------------

phonetisaurus_dir="${this_dir}/phonetisaurus"
if [[ ! -d "${phonetisaurus_dir}/build" ]]; then
    echo "Installing phonetisaurus"
    phonetisaurus_file="${download_dir}/phonetisaurus-2019.tar.gz"

    if [[ ! -f "${phonetisaurus_file}" ]]; then
        phonetisaurus_url='https://github.com/synesthesiam/phonetisaurus-2019/releases/download/v1.0/phonetisaurus-2019.tar.gz'
        echo "Downloading phonetisaurus (${phonetisaurus_url})"
        download "${phonetisaurus_url}" "${phonetisaurus_file}"
    fi

    cd "${this_dir}" && \
        tar -xf "${phonetisaurus_file}" && \
        cd phonetisaurus/ && \
        CXXFLAGS="-I${venv}/include" LDFLAGS="-L${venv}/lib" ./configure "--prefix=${phonetisaurus_dir}/build" && \
        make -j "${make_threads}" && \
        make install
fi

cp -R "${phonetisaurus_dir}"/build/bin/* "${venv}/bin/"

# -----------------------------------------------------------------------------
# Python dependencies
# -----------------------------------------------------------------------------

python3 -m pip install -r "${this_dir}/requirements.txt"

# -----------------------------------------------------------------------------

echo "OK"
