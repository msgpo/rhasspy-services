#!/usr/bin/env bash
set -e

# Script that listens for transcriptions, forwards them to the intent
# recognizer, and then handles the LaunchProgram intent.
#
# Programs are assumed to be in /usr/bin and are automatically detached from the
# terminal when launched.

# -----------------------------------------------------------------------------

# Listen for intent recognized messages in the background
rhasspy-jsonl-sub -t 'rhasspy/intent-recognition/intent-recognized' | \
    while read -r json;
    do
        # Check for the LaunchProgram intent
        intent="$(echo "${json}" | jq -r .intent.name)"
        if [[ "${intent}" == 'LaunchProgram' ]]; then

            # Extract the name of the program to launch
            program="$(echo "${json}" | jq -r .slots.program)"
            if [[ ! -z "${program}" ]]; then
                # Run the program.
                # For simplicity, we assume its the name of a binary in /usr/bin.
                program_exe="/usr/bin/${program}"
                echo "Running ${program_exe}"

                # Detach the process from this terminal, so it will keep running.
                nohup "${program_exe}" &
            fi
        fi
    done &

# Kill the process above when this terminal exits
pid=$!

function finish {
    kill "${pid}"
}

trap finish EXIT

# -----------------------------------------------------------------------------

# Forward transcriptions directly to the intent recognition system.
# This works because the pocketsphinx JSON payload will have a 'text' property
# that is expected by fsticuffs.
rhasspy-jsonl-sub -t 'rhasspy/speech-to-text/text-captured' | \
    mosquitto_pub -t 'rhasspy/intent-recognition/recognize-intent' -l
