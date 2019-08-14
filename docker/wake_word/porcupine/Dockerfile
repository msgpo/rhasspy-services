FROM python:3.6-slim-stretch

RUN apt-get update && \
    apt-get install -y \
        netcat-openbsd \
        mosquitto-clients

ARG PY_DIR=wake_word/porcupine

COPY ${PY_DIR}/requirements.txt /
RUN python3 -m pip install --no-cache-dir -r requirements.txt

COPY bin/rhasspy-yq /usr/bin/
COPY etc/shflags /usr/lib/rhasspy/etc/

COPY ${PY_DIR}/lib/x86_64/libpv_porcupine.so ${PY_DIR}/lib/common/porcupine_params.pv \
     /usr/lib/rhasspy/porcupine/

COPY ${PY_DIR}/resources/keyword_files/linux/porcupine_linux.ppn \
     /usr/lib/rhasspy/porcupine/porcupine.ppn

COPY ${PY_DIR}/bin/rhasspy-* /usr/bin/

COPY ${PY_DIR}/__init__.py ${PY_DIR}/__main__.py /usr/lib/rhasspy/${PY_DIR}/
COPY ${PY_DIR}/porcupine_rhasspy /usr/lib/rhasspy/${PY_DIR}/porcupine_rhasspy/

ENV PYTHONPATH=/usr/lib/rhasspy

ENV porcupine_library=/usr/lib/rhasspy/porcupine/libpv_porcupine.so
ENV porcupine_model=/usr/lib/rhasspy/porcupine/porcupine_params.pv
ENV porcupine_keyword=/usr/lib/rhasspy/porcupine/porcupine.ppn

ENTRYPOINT ["bash"]
