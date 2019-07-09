FROM alpine:latest

RUN apk update && \
    apk add --no-cache \
        bash \
        mosquitto-clients \
        espeak \
        python3 \
        jq

COPY docker/requirements.txt /
RUN python3 -m pip install --no-cache-dir -r /requirements.txt

COPY docker/yq docker/jql /usr/bin/
COPY docker/mqtt docker/shflags /

ENTRYPOINT ["bash"]