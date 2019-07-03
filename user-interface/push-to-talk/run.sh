#!/usr/bin/env bash
host="127.0.0.1"
port="5000"

if [[ ! -z "$2" ]]; then
    host="$1"
    port="$2"
elif [[ ! -z "$1" ]]; then
    port="$1"
fi

python3 -m http.server --bind "${host}" "${port}"
