FROM alpine:latest

RUN apk update
RUN apk add --no-cache bash netcat-openbsd mosquitto-clients python3-dev

COPY requirements.txt /
RUN python3 -m pip install --no-cache-dir -r requirements.txt

COPY main.py docker/run.sh /
ENTRYPOINT ["bash", "run.sh"]
