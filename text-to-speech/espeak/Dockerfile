FROM alpine:latest

RUN apk update
RUN apk add --no-cache bash mosquitto-clients espeak

COPY docker/run.sh /

ENTRYPOINT ["bash", "/run.sh"]