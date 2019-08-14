FROM python:3.6-alpine

RUN apk update && \
    apk add --no-cache \
        bash \
        build-base \
        netcat-openbsd \
        python3-dev \
        swig \
        mosquitto-clients \
        sox jq

ARG PY_DIR=speech_to_text/pocketsphinx

COPY download/pocketsphinx-python.tar.gz /download/
RUN python3 -m pip install --no-cache-dir download/pocketsphinx-python.tar.gz

COPY ${PY_DIR}/requirements.txt /
RUN python3 -m pip install --no-cache-dir -r /requirements.txt

COPY bin/rhasspy-yq /usr/bin/
COPY etc/shflags /usr/lib/rhasspy/etc/

COPY ${PY_DIR}/bin/rhasspy-* /usr/bin/

COPY ${PY_DIR}/__init__.py ${PY_DIR}/__main__.py \
     /usr/lib/rhasspy/${PY_DIR}/

COPY ${PY_DIR}/http_server/ /usr/lib/rhasspy/${PY_DIR}/http_server/
COPY ${PY_DIR}/pocketsphinx_rhasspy/ /usr/lib/rhasspy/${PY_DIR}/pocketsphinx_rhasspy/

ENV PYTHONPATH=/usr/lib/rhasspy

ENTRYPOINT ["bash"]