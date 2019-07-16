FROM alpine AS builder
ARG MAKE_THREADS=8

RUN apk update && \
    apk add build-base autoconf libtool automake bison swig

COPY jsgf_fst_arpa/download/openfst-1.6.9.tar.gz /
RUN tar -xf /openfst-1.6.9.tar.gz && \
    cd /openfst-1.6.9 && \
    ./configure --prefix=/build --enable-far --enable-static --enable-shared --enable-ngram-fsts && \
    make -j $MAKE_THREADS && \
    make install

COPY jsgf_fst_arpa/download/opengrm-ngram-1.3.4.tar.gz /
RUN cd / && tar -xf opengrm-ngram-1.3.4.tar.gz && \
    cd opengrm-ngram-1.3.4/ && \
    CXXFLAGS=-I/build/include \
    LDFLAGS=-L/build/lib \
        ./configure --prefix=/build && \
    make -j $MAKE_THREADS && \
    make install

COPY jsgf_fst_arpa/download/sphinxbase.tar.gz /
RUN cd / && tar -xf /sphinxbase.tar.gz && \
    cd sphinxbase/ && \
    ./autogen.sh && \
    ./configure --prefix=/build && \
    make -j $MAKE_THREADS && \
    make install

COPY jsgf_fst_arpa/download/sphinxtrain.tar.gz /
RUN cd / && tar -xf /sphinxtrain.tar.gz && \
    cd sphinxtrain/ && \
    ./autogen.sh && \
    ./configure --prefix=/build && \
    make -j $MAKE_THREADS && \
    make install

COPY vocab_g2p/download/phonetisaurus-2019.tar.gz /
RUN tar -xf /phonetisaurus-2019.tar.gz && \
    cd /phonetisaurus/ && \
    ./configure --prefix=/build --with-openfst-includes=/build/include --with-openfst-libs=/build/lib && \
    make -j $MAKE_THREADS && \
    make install

FROM alpine

RUN apk update && \
    apk add --no-cache bash mosquitto-clients python3 python3-dev jq

COPY --from=builder /build/bin/* /usr/bin/
COPY --from=builder /build/lib/*.so* /usr/lib/
COPY --from=builder /build/include/ /usr/include/

COPY jsgf_fst_arpa/download/jsgf2fst-0.1.1.tar.gz /

RUN python3 -m pip install --no-cache-dir /jsgf2fst-0.1.1.tar.gz

COPY requirements.txt /
RUN python3 -m pip install --no-cache-dir -r requirements.txt

COPY etc/shflags /etc/
COPY bin/yq bin/jsonl /bin/

COPY docker/ini_jsgf-cli \
     docker/jsgf_fst_arpa-cli \
     docker/vocab_dict-cli \
     docker/vocab_g2p-cli \
     /usr/bin/

COPY ini_jsgf/ini_jsgf /ini_jsgf/ini_jsgf/
COPY jsgf_fst_arpa/jsgf_fst_arpa /jsgf_fst_arpa/jsgf_fst_arpa/
COPY vocab_dict/vocab_dict /vocab_dict/vocab_dict/
COPY vocab_g2p/vocab_g2p /vocab_g2p/vocab_g2p/

COPY ini_jsgf/ini_jsgf-cli /ini_jsgf/
COPY jsgf_fst_arpa/jsgf_fst_arpa-cli /jsgf_fst_arpa/
COPY vocab_dict/vocab_dict-cli /vocab_dict/
COPY vocab_g2p/vocab_g2p-cli /vocab_g2p/

COPY training-mqtt /mqtt

WORKDIR /
ENTRYPOINT ["bash"]
