FROM alpine AS builder
ARG MAKE_THREADS=8

RUN apk update
RUN apk add build-base


COPY download/openfst-1.6.9.tar.gz /
RUN tar -xf /openfst-1.6.9.tar.gz && \
    cd /openfst-1.6.9 && \
    ./configure --prefix=/build --enable-far --enable-static --enable-shared --enable-ngram-fsts && \
    make -j $MAKE_THREADS && \
    make install

FROM alpine

RUN apk update
RUN apk add --no-cache bash mosquitto-clients python3-dev jq 

COPY --from=builder /build/bin/* /usr/bin/
COPY --from=builder /build/lib/*.so* /usr/lib/
COPY --from=builder /build/include/ /usr/include/

COPY download/jsgf2fst-0.1.1.tar.gz /download/
COPY requirements.txt /
RUN python3 -m pip install --no-cache-dir -r /requirements.txt

COPY docker/jql /usr/bin/
COPY main.py docker/run.sh /
ENTRYPOINT ["bash", "/run.sh"]