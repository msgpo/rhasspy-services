#!/usr/bin/env bash
set -e
this_dir="$( cd "$( dirname "$0" )" && pwd )"

# -----------------------------------------------------------------------------

python3 "${this_dir}/main.py" "$@"
