#!/usr/bin/env bash
set -e
this_dir="$( cd "$( dirname "$0" )" && pwd )"
rhasspy_dir="$(realpath "${this_dir}/..")"

log_dir="${this_dir}/logs"
rm -rf "${log_dir}"
mkdir -p "${log_dir}"

# Remove old logs
rm -f "${this_dir}/supervisord.log"

# Directory to write profile files
profile_dir="${this_dir}/profile"

# Load virtual environment
venv="${this_dir}/.venv"
if [[ ! -d "${venv}" ]]; then
    echo "No virtual environment found at ${venv}. Please run install.sh."
    exit 1
fi

source "${venv}/bin/activate"

# -----------------------------------------------------------------------------
# Re-train
# -----------------------------------------------------------------------------

train_dir="${this_dir}/train"
rm -rf "${train_dir}"
mkdir -p "${train_dir}"

# ini -> jsgf
"${rhasspy_dir}/training/ini-jsgf/run.sh" \
    --grammar-dir "${train_dir}/grammars" \
    < "${profile_dir}/sentences.ini"

# jsgf -> fst, arpa
"${rhasspy_dir}/training/jsgf-fst-arpa/run.sh" \
    --grammar-dir "${train_dir}/grammars" \
    --fst "${profile_dir}/intent.fst" \
    --arpa "${profile_dir}/language_model.txt" \
    --vocab "${train_dir}/vocab.txt"

# vocab -> dict
"${rhasspy_dir}/training/vocab-dict/run.sh" \
    --vocab "${train_dir}/vocab.txt" \
    --dictionary "${profile_dir}/base_dictionary.txt" \
    > "${profile_dir}/dictionary.txt"

# -----------------------------------------------------------------------------
# Run assistant
# -----------------------------------------------------------------------------

supervisord -c "${this_dir}/supervisord.conf"
