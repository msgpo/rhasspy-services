#!/usr/bin/env bash
set -e
this_dir="$( cd "$( dirname "$0" )" && pwd )"

if [[ ! -z "$1" ]]; then
    this_dir="$1"
fi

# -----------------------------------------------------------------------------

# Load virtual environment
venv="${this_dir}/.venv"
if [[ -d "${venv}" ]]; then
    source "${venv}/bin/activate"
fi

# -----------------------------------------------------------------------------

# PyInstaller
if [[ -z "$(which pyinstaller)" ]]; then
    echo "Installing PyInstaller"
    python3 -m pip install pyinstaller
fi

cd "${this_dir}" && pyinstaller webrtcvad_rhasspy.spec --noconfirm
