#!/usr/bin/env bash
this_dir="$( cd "$( dirname "$0" )" && pwd )"
rhasspy_dir="$(realpath "${this_dir}/..")"

docker run -it \
       -u "$(id -u):$(id -g)" \
       -v "${this_dir}/nodered:/data" \
       -e FLOWS=/data/lib/flows/local-wake-intent.json \
       -e rhasspy_dir="${rhasspy_dir}" \
       --network host \
       nodered/node-red-docker
