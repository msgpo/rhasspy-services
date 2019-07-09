FROM ubuntu:bionic

RUN apt-get update && \
    apt-get install -y \
        netcat-openbsd \
        python3 python3-pip \
        mosquitto-clients

RUN ln -s /usr/bin/python3 /usr/bin/python

COPY requirements.txt /
RUN python3 -m pip install --no-cache-dir -r requirements.txt

COPY lib/x86_64/libpv_porcupine.so lib/common/porcupine_params.pv /porcupine/
COPY resources/keyword_files/linux/porcupine_linux.ppn /porcupine/porcupine.ppn

COPY docker/yq /usr/bin/
COPY main.py porcupine.py docker/shflags docker/mqtt /

ENTRYPOINT ["bash"]
