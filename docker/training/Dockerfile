FROM alpine AS builder
ARG MAKE_THREADS=8

RUN apk update && \
    apk add build-base \
            autoconf automake libtool \
            bison

# openfst
COPY download/openfst-1.6.9.tar.gz /
RUN tar -xf /openfst-1.6.9.tar.gz && \
    cd /openfst-1.6.9 && \
    ./configure --prefix=/build --enable-far --enable-static --enable-shared --enable-ngram-fsts && \
    make -j $MAKE_THREADS && \
    make install

# opengrm
COPY download/opengrm-ngram-1.3.4.tar.gz /
RUN  tar -xf /opengrm-ngram-1.3.4.tar.gz && \
     cd /opengrm-ngram-1.3.4 && \
     CXXFLAGS=-I/build/include LDFLAGS=-L/build/lib ./configure --prefix=/build && \
     make -j $MAKE_THREADS && \
     make install


# phonetisaurus
COPY download/phonetisaurus-2019.tar.gz /
RUN tar -xf phonetisaurus-2019.tar.gz && \
    cd /phonetisaurus && \
    ./configure --prefix=/build --with-openfst-includes=/build/include --with-openfst-libs=/build/lib && \
    make -j $MAKE_THREADS && \
    make install

# sphinxbase
RUN apk add swig
COPY download/sphinxbase.tar.gz /
RUN tar -xf /sphinxbase.tar.gz && \
    cd /sphinxbase-master && \
    ./autogen.sh --prefix=/build && \
    make -j $MAKE_THREADS && \
    make install

# espeak-ng
COPY download/espeak-ng-1.49.2.tar.gz /
RUN tar -xf /espeak-ng-1.49.2.tar.gz && \
    cd espeak-ng-1.49.2 && \
    ./autogen.sh && \
    ./configure --prefix=/build && \
    make -j $MAKE_THREADS src/espeak-ng src/speak-ng && \
    make install

# -----------------------------------------------------------------------------

FROM alpine

RUN apk update && \
    apk add --no-cache \
        bash \
        python3 \
        python3-dev \
        mosquitto-clients \
        alsa-utils

# Copy pre-built artifacts
COPY --from=builder /build/bin/* /usr/bin/
COPY --from=builder /build/lib/*.so /usr/lib/
COPY --from=builder /build/include/ /usr/include/
COPY --from=builder /build/share/espeak-ng-data /build/share/espeak-ng-data/

# Re-create symbolic links
RUN ln -s /usr/lib/libfstfarscript.so /usr/lib/libfstfarscript.so.13 && \
    ln -s /usr/lib/libfstscript.so /usr/lib/libfstscript.so.13 && \
    ln -s /usr/lib/libfstfar.so /usr/lib/libfstfar.so.13 && \
    ln -s /usr/lib/libfst.so /usr/lib/libfst.so.13 && \
    ln -s /usr/lib/libngram.so /usr/lib/libngram.so.134 && \
    ln -s /usr/lib/libsphinxbase.so /usr/lib/libsphinxbase.so.3 && \
    ln -s /usr/lib/libespeak-ng.so /usr/lib/libespeak-ng.so.1

# jsgf2fst
COPY download/jsgf2fst-0.1.2.tar.gz /download/
RUN python3 -m pip install --no-cache-dir download/jsgf2fst-0.1.2.tar.gz

ARG PY_DIR=training

COPY ${PY_DIR}/requirements.txt /
RUN python3 -m pip install --no-cache-dir -r /requirements.txt

COPY bin/yq /usr/bin/
COPY etc/shflags /etc/

# ini_jsgf
COPY ${PY_DIR}/ini_jsgf/__init__.py ${PY_DIR}/ini_jsgf/__main__.py  /rhasspy/${PY_DIR}/ini_jsgf/
COPY ${PY_DIR}/ini_jsgf/ini_jsgf  /rhasspy/${PY_DIR}/ini_jsgf/ini_jsgf/
COPY ${PY_DIR}/ini_jsgf/bin/ini_jsgf  /usr/bin/

# jsgf_fst_arpa
COPY ${PY_DIR}/jsgf_fst_arpa/__init__.py ${PY_DIR}/jsgf_fst_arpa/__main__.py  /rhasspy/${PY_DIR}/jsgf_fst_arpa/
COPY ${PY_DIR}/jsgf_fst_arpa/jsgf_fst_arpa  /rhasspy/${PY_DIR}/jsgf_fst_arpa/jsgf_fst_arpa/
COPY ${PY_DIR}/jsgf_fst_arpa/bin/jsgf_fst_arpa  /usr/bin/

# vocab_dict
COPY ${PY_DIR}/vocab_dict/__init__.py ${PY_DIR}/vocab_dict/__main__.py  /rhasspy/${PY_DIR}/vocab_dict/
COPY ${PY_DIR}/vocab_dict/vocab_dict  /rhasspy/${PY_DIR}/vocab_dict/vocab_dict/
COPY ${PY_DIR}/vocab_dict/bin/vocab_dict  /usr/bin/

# vocab_g2p
COPY ${PY_DIR}/vocab_g2p/__init__.py ${PY_DIR}/vocab_g2p/__main__.py  /rhasspy/${PY_DIR}/vocab_g2p/
COPY ${PY_DIR}/vocab_g2p/bin/vocab_g2p  /usr/bin/

# train
COPY ${PY_DIR}/__init__.py ${PY_DIR}/__main__.py /rhasspy/${PY_DIR}/
COPY ${PY_DIR}/bin/train  /usr/bin/
COPY ${PY_DIR}/bin/train-mqtt  /usr/bin/

# pronounce
COPY text_to_speech/espeak/bin/espeak_pronounce /usr/bin/

ENV shflags=/etc/shflags
ENV PYTHONPATH=/rhasspy

WORKDIR /rhasspy
ENTRYPOINT ["bash"]