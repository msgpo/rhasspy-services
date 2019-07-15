FROM alpine:latest

RUN apk update && \
    apk add --no-cache \
        bash \
        netcat-openbsd \
        python3 \
        python3-dev \
        swig \
        mosquitto-clients

COPY download/pocketsphinx-python.tar.gz /download/
RUN python3 -m pip install --no-cache-dir download/pocketsphinx-python.tar.gz

COPY requirements.txt /
RUN python3 -m pip install --no-cache-dir -r requirements.txt

COPY bin/yq /bin/
COPY etc/shflags /etc/
COPY pocketsphinx-cli  /
COPY pocketsphinx-mqtt /mqtt
COPY pocketsphinx-http /http
COPY pocketsphinx_rhasspy/ /pocketsphinx_rhasspy/

ENTRYPOINT ["bash"]