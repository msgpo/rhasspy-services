#!/usr/bin/env bash
set -e
this_dir="$( cd "$( dirname "$0" )" && pwd )"
install_dir="${this_dir}"

true_positive="${install_dir}/test/porcupine.wav"
true_negative="${install_dir}/test/what_time_is_it.wav"

function porcupine {
    gst-launch-1.0 filesrc location="$1" ! \
                   wavparse ! \
                   audioconvert ! \
                   audioresample ! \
                   audio/x-raw, rate=16000, channels=1, format=S16LE ! \
                   filesink location=/dev/stdout | \
        "${install_dir}/run.sh" \
            --library lib/x86_64/libpv_porcupine.so \
            --model lib/common/porcupine_params.pv \
            --keyword resources/keyword_files/linux/porcupine_linux.ppn
}

export porcupine

positive_result=$(porcupine "${true_positive}" | jq -r .index)
if [[ "${positive_result}" != "0" ]]; then
    echo "Incorrect positive result (${positive_result})"
    exit 1
fi

negative_result=$(porcupine "${true_negative}")
if [[ ! -z "${negative_result}" ]]; then
    echo "Incorrect negative result (${negative_result})"
    exit 1
fi

echo "OK"
