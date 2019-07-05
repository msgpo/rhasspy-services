#!/usr/bin/env bash
set -e
this_dir="$( cd "$( dirname "$0" )" && pwd )"

# -----------------------------------------------------------------------------

temp_list="$(mktemp)"
function finish {
    rm -f "${temp_list}"
}

trap finish EXIT

# -----------------------------------------------------------------------------

cat > "${temp_list}"
phonetisaurus-apply --word_list "${temp_list}" "$@" | \
    python3 "${this_dir}/main.py"
