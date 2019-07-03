FROM alpine AS builder
ARG MAKE_THREADS=8

RUN apk update
RUN apk add build-base

COPY jsgf-fst-arpa/download/openfst-1.6.9.tar.gz /
RUN tar -xf /openfst-1.6.9.tar.gz && \
    cd /openfst-1.6.9 && \
    ./configure --prefix=/build --enable-far --enable-static --enable-shared --enable-ngram-fsts && \
    make -j $MAKE_THREADS && \
    make install

COPY jsgf-fst-arpa/download/opengrm-ngram-1.3.4.tar.gz /
RUN cd / && tar -xf opengrm-ngram-1.3.4.tar.gz && \
    cd opengrm-ngram-1.3.4/ && \
    CXXFLAGS=-I/build/include \
    LDFLAGS=-L/build/lib \
        ./configure --prefix=/build && \
    make -j $MAKE_THREADS && \
    make install

RUN apk add autoconf libtool automake bison swig

COPY jsgf-fst-arpa/download/sphinxbase.tar.gz /
RUN cd / && tar -xf /sphinxbase.tar.gz && \
    cd sphinxbase/ && \
    ./autogen.sh && \
    ./configure --prefix=/build && \
    make -j $MAKE_THREADS && \
    make install

COPY jsgf-fst-arpa/download/sphinxtrain.tar.gz /
RUN cd / && tar -xf /sphinxtrain.tar.gz && \
    cd sphinxtrain/ && \
    ./autogen.sh && \
    ./configure --prefix=/build && \
    make -j $MAKE_THREADS && \
    make install

FROM alpine

RUN apk update
RUN apk add --no-cache bash mosquitto-clients python3-dev 

COPY --from=builder /build/bin/* /usr/bin/
COPY --from=builder /build/lib/*.so* /usr/lib/
COPY --from=builder /build/include/ /usr/include/

COPY jsgf-fst-arpa/download/jsgf2fst-0.1.1.tar.gz \
     jsgf-fst-arpa/download/pyjsgf-1.6.0.tar.gz \
     /download/

COPY docker/requirements.txt /
RUN python3 -m pip install --no-cache-dir -r requirements.txt

COPY ini-jsgf/main.py /ini-jsgf.py
COPY jsgf-fst-arpa/main.py /jsgf-fst-arpa.py
COPY vocab-dict/main.py /vocab-dict.py

COPY docker/run.sh /
ENTRYPOINT ["bash", "/run.sh"]
