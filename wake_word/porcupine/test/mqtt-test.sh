#!/usr/bin/env bash
set -e
this_dir="$( cd "$( dirname "$0" )" && pwd )"

mqtt_host='127.0.0.1'
mqtt_port=1883
audio_host="${mqtt_host}"
audio_port=5000
audio_files=("${this_dir}/porcupine.wav")

# Print responses when received
(timeout 5s \
         mosquitto_sub -h "${mqtt_host}" -p "${mqtt_port}" \
         -v -t 'rhasspy/wake-word/detected/#' -C "${#audio_files[@]}" && \
     echo 'OK') &

for audio_file in "${audio_files[@]}";
do
    name="$(basename "${audio_file}" .wav)"

    # Start listening
    echo "${audio_file}"
    mosquitto_pub -h "${mqtt_host}" -p "${mqtt_port}" \
                  -t "rhasspy/wake-word/start-listening/${name}" -m '{}'

    # Send audio
    gst-launch-1.0 -q \
        filesrc location="${audio_file}" ! \
        decodebin ! \
        audioconvert ! \
        audioresample ! \
        audio/x-raw, rate=16000, channels=1, format=S16LE ! \
        udpsink host="${audio_host}" port="${audio_port}"

    sleep 1

    # Stop listening
    mosquitto_pub -h "${mqtt_host}" -p "${mqtt_port}" \
                  -t "rhasspy/wake-word/stop-listening/${name}" -m '{}'
done

# Wait for response
wait
