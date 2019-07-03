FROM alpine:latest

RUN apk update
RUN apk add --no-cache bash netcat-openbsd python3-dev swig

COPY download/pocketsphinx-python.tar.gz /download/
COPY requirements.txt /
RUN python3 -m pip install --no-cache-dir -r requirements.txt

COPY main.py docker/run.sh /
ENTRYPOINT ["bash", "run.sh"]