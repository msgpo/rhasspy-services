FROM alpine AS builder
ARG MAKE_THREADS=8

RUN apk update && \
    apk add build-base

COPY download/openfst-1.6.9.tar.gz /
RUN tar -xf /openfst-1.6.9.tar.gz && \
    cd /openfst-1.6.9 && \
    ./configure --prefix=/build --enable-far --enable-static --enable-shared --enable-ngram-fsts && \
    make -j $MAKE_THREADS && \
    make install

FROM alpine

RUN apk update && \
    apk add --no-cache bash mosquitto-clients python3-dev jq 

COPY --from=builder /build/bin/* /usr/bin/
COPY --from=builder /build/lib/*.so* /usr/lib/
COPY --from=builder /build/include/ /usr/include/

COPY download/jsgf2fst-0.1.2.tar.gz /download/
RUN python3 -m pip install --no-cache-dir download/jsgf2fst-0.1.2.tar.gz

ARG PY_DIR=intent_recognition/fsticuffs

COPY ${PY_DIR}/requirements.txt /
RUN python3 -m pip install --no-cache-dir -r /requirements.txt

COPY bin/yq /usr/bin/
COPY etc/shflags /etc/

COPY ${PY_DIR}/bin/fsticuffs /usr/bin/
COPY ${PY_DIR}/bin/fsticuffs-mqtt /usr/bin/mqtt
COPY ${PY_DIR}/bin/fsticuffs-http /usr/bin/http

COPY ${PY_DIR}/__init__.py ${PY_DIR}/__main__.py /rhasspy/${PY_DIR}/
COPY ${PY_DIR}/fsticuffs /rhasspy/${PY_DIR}/fsticuffs/

ENV shflags=/etc/shflags
ENV PYTHONPATH=/rhasspy

ENTRYPOINT ["bash"]