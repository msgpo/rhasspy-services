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

COPY bin/yq /usr/bin/
COPY etc/shflags /etc/

COPY ${PY_DIR}/bin/webrtcvad /usr/bin/
COPY ${PY_DIR}/bin/webrtcvad-mqtt /usr/bin/mqtt

COPY ${PY_DIR}/__init__.py ${PY_DIR}/__main__.py /rhasspy/${PY_DIR}/
COPY ${PY_DIR}/webrtcvad_rhasspy /rhasspy/voice_command/webrtcvad/webrtcvad_rhasspy/

ENV shflags=/etc/shflags
ENV PYTHONPATH=/rhasspy

WORKDIR /rhasspy
ENTRYPOINT ["bash"]
