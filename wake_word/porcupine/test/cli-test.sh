#!/usr/bin/env bash
set -e
this_dir="$( cd "$( dirname "$0" )" && pwd )"

true_positive="${this_dir}/porcupine.raw"
true_negative="${this_dir}/what_time_is_it.raw"

function porcupine_test {
    cat "$1" | \
        rhasspy-porcupine \
            --library "${this_dir}/../lib/x86_64/libpv_porcupine.so" \
            --model "${this_dir}/../lib/common/porcupine_params.pv" \
            --keyword "${this_dir}/../resources/keyword_files/linux/porcupine_linux.ppn"
}

export porcupine_test

positive_result=$(porcupine_test "${true_positive}" | jq -r .index)
if [[ "${positive_result}" != "0" ]]; then
    echo "Incorrect positive result (${positive_result})"
    exit 1
fi

negative_result=$(porcupine_test "${true_negative}")
if [[ ! -z "${negative_result}" ]]; then
    echo "Incorrect negative result (${negative_result})"
    exit 1
fi

echo "OK"
