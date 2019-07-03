#!/usr/bin/env bash
set -e
this_dir="$( cd "$( dirname "$0" )" && pwd )"
RHASSPY_DIR="$(realpath "${this_dir}/..")"

log_dir="${this_dir}/logs"
mkdir -p "${log_dir}"

# Remove old logs
rm -f "${log_dir}/*.log"
rm -f "${this_dir}/supervisord.log"

# Directory to write profile files
profile_dir="${this_dir}/profile"

# -----------------------------------------------------------------------------
# Re-train
# -----------------------------------------------------------------------------

train_dir="${this_dir}/train"
rm -rf "${train_dir}"
mkdir -p "${train_dir}"

# ini -> jsgf
"${RHASSPY_DIR}/training/ini-jsgf/run.sh" \
    --grammar-dir "${train_dir}/grammars" \
    < "${profile_dir}/sentences.ini"

# jsgf -> fst, arpa
"${RHASSPY_DIR}/training/jsgf-fst-arpa/run.sh" \
    --grammar-dir "${train_dir}/grammars" \
    --fst "${profile_dir}/intent.fst" \
    --arpa "${profile_dir}/language_model.txt" \
    --vocab "${train_dir}/vocab.txt"

# vocab -> dict
"${RHASSPY_DIR}/training/vocab-dict/run.sh" \
    --vocab "${train_dir}/vocab.txt" \
    --dictionary "${profile_dir}/base_dictionary.txt" \
    > "${profile_dir}/dictionary.txt"

# -----------------------------------------------------------------------------
# Run assistant
# -----------------------------------------------------------------------------

supervisord -c "${this_dir}/supervisord.conf"
