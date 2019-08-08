FROM alpine:latest

RUN apk update && \
    apk add --no-cache \
        bash \
        netcat-openbsd \
        python3 python3-dev \
        swig \
        mosquitto-clients \
        sox jq

ARG PY_DIR=speech_to_text/pocketsphinx

COPY download/pocketsphinx-python.tar.gz /download/
RUN python3 -m pip install --no-cache-dir download/pocketsphinx-python.tar.gz

COPY ${PY_DIR}/requirements.txt /
RUN python3 -m pip install --no-cache-dir -r /requirements.txt

COPY bin/yq /usr/bin/
COPY etc/shflags /etc/

COPY ${PY_DIR}/bin/pocketsphinx ${PY_DIR}/bin/pocketsphinx_wavs2text  /usr/bin/
COPY ${PY_DIR}/bin/pocketsphinx-mqtt /usr/bin/mqtt
COPY ${PY_DIR}/bin/pocketsphinx-http /usr/bin/http

COPY ${PY_DIR}/__init__.py ${PY_DIR}/__main__.py /rhasspy/${PY_DIR}/
COPY ${PY_DIR}/http_server/ /rhasspy/${PY_DIR}/http_server/
COPY ${PY_DIR}/pocketsphinx_rhasspy/ /rhasspy/${PY_DIR}/pocketsphinx_rhasspy/

ENV shflags=/etc/shflags
ENV PYTHONPATH=/rhasspy

WORKDIR /rhasspy
ENTRYPOINT ["bash"]