FROM ubuntu:bionic

RUN apt-get update && \
    apt-get install -y \
        netcat-openbsd \
        python3 python3-pip \
        mosquitto-clients

COPY requirements.txt /
RUN python3 -m pip install --no-cache-dir -r requirements.txt

COPY lib/x86_64/libpv_porcupine.so lib/common/porcupine_params.pv /porcupine/
COPY resources/keyword_files/linux/porcupine_linux.ppn /porcupine/porcupine.ppn

COPY bin/yq /bin/
COPY etc/shflags /etc/
COPY porcupine.py porcupine-cli /
COPY porcupine-mqtt /mqtt
COPY porcupine_rhasspy /porcupine_rhasspy/

ENTRYPOINT ["bash"]
