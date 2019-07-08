FROM alpine:latest

RUN apk update
RUN apk add --no-cache bash netcat-openbsd python3-dev swig mosquitto-clients

COPY download/pocketsphinx-python.tar.gz /download/
COPY requirements.txt /
RUN python3 -m pip install --no-cache-dir -r requirements.txt

COPY docker/mqtt docker/http docker/yq /usr/bin/
COPY main.py docker/http_server.py /

ENTRYPOINT ["bash"]