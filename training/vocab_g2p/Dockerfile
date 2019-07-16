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

COPY download/phonetisaurus-2019.tar.gz /
RUN tar -xf /phonetisaurus-2019.tar.gz && \
    cd /phonetisaurus/ && \
    ./configure --prefix=/build --with-openfst-includes=/build/include --with-openfst-libs=/build/lib && \
    make -j $MAKE_THREADS && \
    make install

FROM alpine

RUN apk update
RUN apk add --no-cache bash mosquitto-clients jq python3

COPY --from=builder /build/bin/* /usr/bin/
COPY --from=builder /build/lib/*.so* /usr/lib/

COPY requirements.txt /
RUN python3 -m pip install -r /requirements.txt

COPY main.py docker/run.sh /
ENTRYPOINT ["bash", "/run.sh"]