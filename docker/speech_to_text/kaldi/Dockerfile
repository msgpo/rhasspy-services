FROM ubuntu:bionic AS builder

ARG MAKE_THREADS=8

RUN apt-get update && \
    apt-get install -y build-essential \
        zlib1g-dev unzip \
        automake autoconf libtool \
        git wget subversion sox \
        python2.7 python3 \
        libatlas-dev libatlas3-base

RUN ln -s /usr/bin/python2.7 /usr/bin/python2

COPY etc/kaldi/tools.Makefile.patch /

COPY download/kaldi.tar.gz /
RUN tar -xf /kaldi.tar.gz && \
    patch /kaldi-master/tools/Makefile /tools.Makefile.patch

COPY download/kaldi/* /kaldi-master/tools/
RUN cd /kaldi-master/tools && \
    make -j $MAKE_THREADS

RUN cd /kaldi-master/src && \
    ./configure --shared --mathlib=ATLAS && \
    make depend -j $MAKE_THREADS && \
    make -j $MAKE_THREADS

# -----------------------------------------------------------------------------

FROM ubuntu:bionic

RUN apt-get update && \
    apt-get install -y \
        python3 python3-pip \
        libatlas3-base \
        sox bc jq

COPY --from=builder /kaldi-master/egs/wsj/s5 /kaldi/egs/wsj/s5/
COPY --from=builder /kaldi-master/tools/openfst-1.6.7/lib/*.so /kaldi/tools/openfst/lib/
COPY --from=builder /kaldi-master/tools/openfst-1.6.7/bin /kaldi/tools/openfst/bin/
COPY --from=builder /kaldi-master/src/lib/*.so /kaldi/src/lib/
COPY --from=builder /kaldi-master/src/bin /kaldi/src/bin/
COPY --from=builder /kaldi-master/src/fstbin /kaldi/src/fstbin/
COPY --from=builder /kaldi-master/src/lmbin /kaldi/src/lmbin/
COPY --from=builder /kaldi-master/src/gmmbin /kaldi/src/gmmbin/
COPY --from=builder /kaldi-master/src/featbin /kaldi/src/featbin/
COPY --from=builder /kaldi-master/src/online2bin /kaldi/src/online2bin/

# Re-create symbolic links
RUN ln -s /kaldi/tools/openfst/lib/libfstfarscript.so /kaldi/tools/openfst/lib/libfstfarscript.so.10 && \
    ln -s /kaldi/tools/openfst/lib/libfstscript.so /kaldi/tools/openfst/lib/libfstscript.so.10 && \
    ln -s /kaldi/tools/openfst/lib/libfstfar.so /kaldi/tools/openfst/lib/libfstfar.so.10 && \
    ln -s /kaldi/tools/openfst/lib/libfst.so /kaldi/tools/openfst/lib/libfst.so.10

ENV PY_DIR=speech_to_text/kaldi

COPY ${PY_DIR}/requirements.txt /
RUN python3 -m pip install --no-cache-dir -r /requirements.txt

COPY bin/yq /usr/bin/
COPY etc/shflags /etc/

COPY ${PY_DIR}/__main__.py /rhasspy/${PY_DIR}/
COPY ${PY_DIR}/bin/kaldi /usr/bin/
COPY ${PY_DIR}/bin/kaldi-decode /usr/bin/
COPY training/bin/kaldi-train /usr/bin/

ENV shflags=/etc/shflags
ENV PYTHONPATH=/rhasspy
ENV kaldi_dir=/kaldi

WORKDIR /rhasspy
ENTRYPOINT ["bash"]