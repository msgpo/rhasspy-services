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

COPY bin/yq bin/jsonl bin/jsonl_sub /usr/bin/
COPY etc/shflags /etc/
COPY ${PY_DIR}/bin/espeak-mqtt /

ENV shflags=/etc/shflags

WORKDIR /
ENTRYPOINT ["bash", "/espeak-mqtt"]