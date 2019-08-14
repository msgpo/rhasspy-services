FROM alpine:latest

RUN apk update && \
    apk add --no-cache \
        bash \
        mosquitto-clients \
        espeak \
        python3 \
        jq

ARG PY_DIR=text_to_speech/espeak

COPY ${PY_DIR}/requirements.txt /
RUN python3 -m pip install --no-cache-dir -r /requirements.txt

COPY bin/rhasspy-yq bin/rhasspy-jsonl-sub /usr/bin/
COPY etc/shflags /usr/lib/rhasspy/etc/

COPY ${PY_DIR}/bin/rhasspy-* /usr/bin/

ENTRYPOINT ["bash"]