FROM ubuntu:bionic

RUN apt-get update
RUN apt-get install -y netcat-openbsd python3 python3-pip mosquitto-clients
RUN ln -s /usr/bin/python3 /usr/bin/python

COPY requirements.txt /
RUN python3 -m pip install --no-cache-dir -r requirements.txt

COPY lib /porcupine/lib
COPY resources /porcupine/resources
COPY main.py porcupine.py docker/run.sh /
ENTRYPOINT ["bash", "run.sh"]
