FROM alpine:latest

RUN apk update && \
    apk add --no-cache \
        bash \
        mosquitto-clients \
        espeak \
        python3 \
        jq

COPY requirements.txt /
RUN python3 -m pip install --no-cache-dir -r /requirements.txt

COPY bin/yq bin/jql /bin/
COPY etc/shflags /etc/
COPY espeak-mqtt /mqtt

WORKDIR /
ENTRYPOINT ["bash"]