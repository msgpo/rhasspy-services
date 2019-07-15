FROM alpine:latest

RUN apk update && \
    apk add --no-cache \
        bash \
        netcat-openbsd \
        mosquitto-clients \
        python3-dev

COPY requirements.txt /
RUN python3 -m pip install --no-cache-dir -r requirements.txt

COPY bin/yq /bin/
COPY etc/shflags /etc/
COPY webrtcvad-cli /
COPY webrtcvad-mqtt /mqtt
COPY webrtcvad_rhasspy /webrtcvad_rhasspy/

ENTRYPOINT ["bash"]
