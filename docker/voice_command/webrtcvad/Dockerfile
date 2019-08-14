FROM alpine:latest

RUN apk update && \
    apk add --no-cache \
        bash \
        netcat-openbsd \
        mosquitto-clients \
        python3-dev

ARG PY_DIR=voice_command/webrtcvad

COPY ${PY_DIR}/requirements.txt /
RUN python3 -m pip install --no-cache-dir -r requirements.txt

COPY bin/rhasspy-yq /usr/bin/
COPY etc/shflags /usr/lib/rhasspy/etc/

COPY ${PY_DIR}/bin/rhasspy-* /usr/bin/

COPY ${PY_DIR}/__init__.py ${PY_DIR}/__main__.py \
     /usr/lib/rhasspy/${PY_DIR}/

COPY ${PY_DIR}/webrtcvad_rhasspy /usr/lib/rhasspy/${PY_DIR}/webrtcvad_rhasspy/

ENV PYTHONPATH=/usr/lib/rhasspy

ENTRYPOINT ["bash"]
