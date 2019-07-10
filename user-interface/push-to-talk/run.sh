#!/usr/bin/env bash
set -e
this_dir="$( cd "$( dirname "$0" )" && pwd )"
install_dir="${this_dir}"

host="127.0.0.1"
port="12101"

if [[ ! -z "$2" ]]; then
    host="$1"
    port="$2"
elif [[ ! -z "$1" ]]; then
    port="$1"
fi

cd "${this_dir}" && python3 -m http.server --bind "${host}" "${port}"
