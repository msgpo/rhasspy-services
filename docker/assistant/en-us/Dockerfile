FROM python:3.6-slim-stretch AS builder
ARG MAKE_THREADS=8

RUN apt-get update && \
    apt-get install -y \
        build-essential \
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

# -----------------------------------------------------------------------------

FROM python:3.6-slim-stretch

RUN apt-get update && \
    apt-get install -y \
        build-essential \
        python3-dev \
        mosquitto-clients \
        sphinxbase-utils \
        espeak-ng \
        swig \
        netcat \
        jq \
        sox

# Copy pre-built artifacts
COPY --from=builder /build/bin/* /usr/bin/
COPY --from=builder /build/lib/*.so /usr/lib/
COPY --from=builder /build/include/ /usr/include/

# Re-create symbolic links
RUN ln -s /usr/lib/libfstfarscript.so /usr/lib/libfstfarscript.so.13 && \
    ln -s /usr/lib/libfstscript.so /usr/lib/libfstscript.so.13 && \
    ln -s /usr/lib/libfstfar.so /usr/lib/libfstfar.so.13 && \
    ln -s /usr/lib/libfst.so /usr/lib/libfst.so.13 && \
    ln -s /usr/lib/libngram.so /usr/lib/libngram.so.134 && \
    ln -s /usr/lib/libsphinxbase.so /usr/lib/libsphinxbase.so.3

# -----------------------------------------------------------------------------
# Training
# -----------------------------------------------------------------------------

# jsgf2fst
COPY download/jsgf2fst-0.1.2.tar.gz /download/
RUN python3 -m pip install --no-cache-dir download/jsgf2fst-0.1.2.tar.gz

COPY training/requirements.txt /requirements.training.txt
RUN python3 -m pip install --no-cache-dir -r /requirements.training.txt

COPY bin/rhasspy-yq /usr/bin/
COPY etc/shflags /usr/lib/rhasspy/etc/

# ini_jsgf
COPY training/ini_jsgf/__init__.py training/ini_jsgf/__main__.py \
     /usr/lib/rhasspy/training/ini_jsgf/

COPY training/ini_jsgf/ini_jsgf /usr/lib/rhasspy/training/ini_jsgf/ini_jsgf/
COPY training/ini_jsgf/bin/rhasspy-ini_jsgf /usr/bin/

# jsgf_fst_arpa
COPY training/jsgf_fst_arpa/__init__.py training/jsgf_fst_arpa/__main__.py \
     /usr/lib/rhasspy/training/jsgf_fst_arpa/

COPY training/jsgf_fst_arpa/jsgf_fst_arpa /usr/lib/rhasspy/training/jsgf_fst_arpa/jsgf_fst_arpa/
COPY training/jsgf_fst_arpa/bin/rhasspy-jsgf_fst_arpa /usr/bin/

# vocab_dict
COPY training/vocab_dict/__init__.py training/vocab_dict/__main__.py \
     /usr/lib/rhasspy/training/vocab_dict/

COPY training/vocab_dict/vocab_dict /usr/lib/rhasspy/training/vocab_dict/vocab_dict/
COPY training/vocab_dict/bin/rhasspy-vocab_dict /usr/bin/

# vocab_g2p
COPY training/vocab_g2p/__init__.py training/vocab_g2p/__main__.py \
     /usr/lib/rhasspy/training/vocab_g2p/

COPY training/vocab_g2p/bin/rhasspy-vocab_g2p  /usr/bin/

# train
COPY training/__init__.py /usr/lib/rhasspy/training/
COPY training/bin/rhasspy-*  /usr/bin/

# pronounce
COPY text_to_speech/espeak/bin/espeak_pronounce /usr/bin/

# -----------------------------------------------------------------------------
# Speech To Text
# -----------------------------------------------------------------------------

COPY download/pocketsphinx-python.tar.gz /download/
RUN python3 -m pip install --no-cache-dir download/pocketsphinx-python.tar.gz

COPY speech_to_text/pocketsphinx/requirements.txt /requirements.pocketsphinx.txt
RUN python3 -m pip install --no-cache-dir -r /requirements.pocketsphinx.txt

COPY bin/rhasspy-yq /usr/bin/
COPY etc/shflags /usr/lib/rhasspy/etc/

COPY speech_to_text/pocketsphinx/bin/rhasspy-* /usr/bin/

COPY speech_to_text/pocketsphinx/__init__.py speech_to_text/pocketsphinx/__main__.py \
     /usr/lib/rhasspy/speech_to_text/pocketsphinx/

COPY speech_to_text/pocketsphinx/http_server/ \
     /usr/lib/rhasspy/speech_to_text/pocketsphinx/http_server/

COPY speech_to_text/pocketsphinx/pocketsphinx_rhasspy/ \
     /usr/lib/rhasspy/speech_to_text/pocketsphinx/pocketsphinx_rhasspy/

# -----------------------------------------------------------------------------
# Intent Recognition
# -----------------------------------------------------------------------------

COPY download/jsgf2fst-0.1.2.tar.gz /download/
RUN python3 -m pip install --no-cache-dir download/jsgf2fst-0.1.2.tar.gz

ARG PY_DIR=intent_recognition/fsticuffs

COPY intent_recognition/fsticuffs/requirements.txt /requirements.fsticuffs.txt
RUN python3 -m pip install --no-cache-dir -r /requirements.fsticuffs.txt

COPY bin/rhasspy-yq /usr/bin/
COPY etc/shflags /usr/lib/rhasspy/etc/

COPY intent_recognition/fsticuffs/bin/rhasspy-* /usr/bin/

COPY intent_recognition/fsticuffs/__init__.py \
     intent_recognition/fsticuffs/__main__.py \
     /usr/lib/rhasspy/intent_recognition/fsticuffs/

COPY intent_recognition/fsticuffs/fsticuffs \
     /usr/lib/rhasspy/intent_recognition/fsticuffs/fsticuffs/

# -----------------------------------------------------------------------------
# Voice Command
# -----------------------------------------------------------------------------

COPY voice_command/webrtcvad/requirements.txt /requirements.webrtcvad.txt
RUN python3 -m pip install --no-cache-dir -r requirements.webrtcvad.txt

COPY bin/rhasspy-yq /usr/bin/
COPY etc/shflags /usr/lib/rhasspy/etc/

COPY voice_command/webrtcvad/bin/rhasspy-* /usr/bin/

COPY voice_command/webrtcvad/__init__.py voice_command/webrtcvad/__main__.py \
     /usr/lib/rhasspy/voice_command/webrtcvad/

COPY voice_command/webrtcvad/webrtcvad_rhasspy \
     /usr/lib/rhasspy/voice_command/webrtcvad/webrtcvad_rhasspy/

# -----------------------------------------------------------------------------
# Wake Word
# -----------------------------------------------------------------------------

COPY wake_word/porcupine/requirements.txt /requirements.porcupine.txt
RUN python3 -m pip install --no-cache-dir -r requirements.porcupine.txt

COPY bin/rhasspy-yq /usr/bin/
COPY etc/shflags /usr/lib/rhasspy/etc/

COPY wake_word/porcupine/lib/x86_64/libpv_porcupine.so \
     /usr/lib/rhasspy/wake_word/porcupine/lib/

COPY wake_word/porcupine/lib/common/porcupine_params.pv \
     /usr/lib/rhasspy/wake_word/porcupine/lib/common/

COPY wake_word/porcupine/resources/keyword_files/linux/porcupine_linux.ppn \
     /usr/lib/rhasspy/wake_word/porcupine/keyword_files/linux/

COPY wake_word/porcupine/bin/rhasspy-* /usr/bin/

COPY wake_word/porcupine/__init__.py wake_word/porcupine/__main__.py \
     /usr/lib/rhasspy/wake_word/porcupine/

COPY wake_word/porcupine/porcupine_rhasspy \
     /usr/lib/rhasspy/wake_word/porcupine/porcupine_rhasspy/

ENV porcupine_library=/usr/lib/rhasspy/wake_word/porcupine/lib/libpv_porcupine.so
ENV porcupine_model=/usr/lib/rhasspy/wake_word/porcupine/lib/common/porcupine_params.pv
ENV porcupine_keyword=/usr/lib/rhasspy/wake_word/porcupine/keyword_files/linux/porcupine_linux.ppn

# -----------------------------------------------------------------------------

ENV PYTHONPATH=/usr/lib/rhasspy

ENTRYPOINT ["bash"]