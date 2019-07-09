FROM alpine:latest

RUN apk update && \
    apk add --no-cache \
        bash \
        netcat-openbsd \
        mosquitto-clients \
        python3-dev

COPY requirements.txt /
RUN python3 -m pip install --no-cache-dir -r requirements.txt

COPY docker/yq /usr/bin/
COPY main.py docker/mqtt docker/shflags /

ENTRYPOINT ["bash"]
