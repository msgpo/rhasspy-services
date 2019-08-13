FROM python:3.6-slim-stretch

RUN apt-get update && \
    apt-get install -y \
        netcat-openbsd \
        mosquitto-clients

ARG PY_DIR=wake_word/porcupine

COPY ${PY_DIR}/requirements.txt /
RUN python3 -m pip install --no-cache-dir -r requirements.txt

COPY bin/yq /usr/bin/
COPY etc/shflags /etc/

COPY ${PY_DIR}/lib/x86_64/libpv_porcupine.so ${PY_DIR}/lib/common/porcupine_params.pv /etc/porcupine/
COPY ${PY_DIR}/resources/keyword_files/linux/porcupine_linux.ppn /etc/porcupine/porcupine.ppn

COPY ${PY_DIR}/bin/porcupine /usr/bin/
COPY ${PY_DIR}/bin/porcupine-mqtt /usr/bin/mqtt

COPY ${PY_DIR}/__init__.py ${PY_DIR}/__main__.py /rhasspy/${PY_DIR}/
COPY ${PY_DIR}/porcupine_rhasspy /rhasspy/${PY_DIR}/porcupine_rhasspy/

ENV shflags=/etc/shflags
ENV PYTHONPATH=/rhasspy

ENV porcupine_library=/etc/porcupine/libpv_porcupine.so
ENV porcupine_model=/etc/porcupine/porcupine_params.pv
ENV porcupine_keyword=/etc/porcupine/porcupine.ppn

ENTRYPOINT ["bash"]
