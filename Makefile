.PHONY: debian-assistant-en-us \
        debian-audio \
        debian-espeak \
        debian-fsticuffs \
        debian-kaldi \
        debian-languages \
        debian-pocketsphinx \
        debian-porcupine \
        debian-train \
        docker-assistant-en-us \
        docker-espeak \
        docker-fsticuffs \
        docker-kaldi \
        docker-pocketsphinx \
        docker-training \
        docker-porcupine \
        docker-pulseaudio-input \
        docker-pulseaudio-output \
        docker-push-to-talk \
        docker-webrtcvad \
        installer-fsticuffs \
        installer-kaldi \
        installer-pocketsphinx \
        installer-porcupine \
        installer-train \
        installer-webrtcvad \
        installer-yq

# -----------------------------------------------------------------------------

CPU_ARCH ?= x86_64
FRIENDLY_ARCH ?= amd64

# -----------------------------------------------------------------------------
# Docker
# -----------------------------------------------------------------------------

docker-assistant-en-us:
	docker build . -f docker/assistant/en-us/Dockerfile -t rhasspy/assistant/en-us

docker-espeak:
	docker build . -f docker/text_to_speech/espeak/Dockerfile -t rhasspy/text-to-speech/espeak

docker-fsticuffs:
	docker build . -f docker/intent_recognition/fsticuffs/Dockerfile -t rhasspy/intent-recognition/fsticuffs

docker-kaldi:
	docker build . -f docker/speech_to_text/kaldi/Dockerfile -t rhasspy/speech-to-text/kaldi

docker-pocketsphinx:
	docker build . -f docker/speech_to_text/pocketsphinx/Dockerfile -t rhasspy/speech-to-text/pocketsphinx

docker-training:
	docker build . -f docker/training/Dockerfile -t rhasspy/training

docker-porcupine:
	docker build . -f docker/wake_word/porcupine/Dockerfile -t rhasspy/wake-word/porcupine

docker-pulseaudio-input:
	docker build . -f docker/audio_input/pulseaudio/Dockerfile -t rhasspy/audio-input/pulseaudio

docker-pulseaudio-output:
	docker build . -f docker/audio_output/pulseaudio/Dockerfile -t rhasspy/audio-output/pulseaudio

docker-push-to-talk:
	docker build . -f docker/user_interface/push-to-talk/Dockerfile -t rhasspy/user_interface/push-to-talk

docker-webrtcvad:
	docker build . -f docker/voice_command/webrtcvad//Dockerfile -t rhasspy/voice-command/webrtcvad

# -----------------------------------------------------------------------------
# PyInstaller
# -----------------------------------------------------------------------------

installer-fsticuffs:
	bash build.sh installer/intent_recognition/fsticuffs.spec

installer-kaldi:
	bash build.sh installer/speech_to_text/kaldi.spec

installer-pocketsphinx:
	bash build.sh installer/speech_to_text/pocketsphinx.spec
	bash build.sh installer/speech_to_text/pocketsphinx-http.spec

installer-porcupine:
	bash build.sh installer/wake_word/porcupine.spec

installer-train:
	bash build.sh installer/training/ini_jsgf.spec
	bash build.sh installer/training/vocab_g2p.spec
	bash build.sh installer/training/vocab_dict.spec
	bash build.sh installer/training/jsgf_fst_arpa.spec
	bash build.sh installer/training/train.spec

installer-webrtcvad:
	bash build.sh installer/voice_command/webrtcvad.spec

installer-utils:
	bash build.sh installer/yq.spec
	bash build.sh installer/jsonl-sub.spec

# -----------------------------------------------------------------------------
# Debian
# -----------------------------------------------------------------------------

debian-assistant-en-us:
	cd debian/assistant && fakeroot dpkg --build rhasspy-assistant-en-us_1.0_$(FRIENDLY_ARCH)

debian-audio:
	cd debian/audio && fakeroot dpkg --build rhasspy-pulseaudio_1.0_$(FRIENDLY_ARCH)

debian-espeak:
	cd debian/text_to_speech && fakeroot dpkg --build rhasspy-espeak_1.0_$(FRIENDLY_ARCH)

debian-fsticuffs: installer-fsticuffs
	bash debianize.sh intent_recognition fsticuffs $(FRIENDLY_ARCH)

debian-kaldi: installer-kaldi
	bash debianize.sh speech_to_text kaldi $(FRIENDLY_ARCH)

debian-languages:
	output_dir="debian/languages/rhasspy-en-us-pocketsphinx-cmu_1.0_all/usr/lib/rhasspy/languages/english/en-us_pocketsphinx-cmu/"; \
    mkdir -p "$${output_dir}" && \
    rsync -av --delete languages/english/en-us_pocketsphinx-cmu/ "$${output_dir}/"
	cd debian/languages && fakeroot dpkg --build rhasspy-en-us-pocketsphinx-cmu_1.0_all

debian-pocketsphinx: installer-pocketsphinx
	output_dir="debian/speech_to_text/rhasspy-pocketsphinx_1.0_$(FRIENDLY_ARCH)/usr/lib/rhasspy/pocketsphinx-http"; \
    mkdir -p "$${output_dir}" && \
    rsync -av --delete dist/pocketsphinx-http/ "$${output_dir}/"
	bash debianize.sh speech_to_text pocketsphinx $(FRIENDLY_ARCH)

debian-porcupine: installer-porcupine
	bash debianize.sh wake_word porcupine $(FRIENDLY_ARCH)

debian-train: installer-train
	rsync -av dist/ini_jsgf/ dist/vocab_g2p/ dist/vocab_dict/ dist/jsgf_fst_arpa/ dist/train/
	bash debianize.sh training train $(FRIENDLY_ARCH)

debian-utils: installer-utils
	bash debianize.sh utils yq $(FRIENDLY_ARCH)
	bash debianize.sh utils jsonl-sub $(FRIENDLY_ARCH)

debian-webrtcvad: installer-webrtcvad
	bash debianize.sh voice_command webrtcvad $(FRIENDLY_ARCH)

# -----------------------------------------------------------------------------
# Multi-Arch Builds
# -----------------------------------------------------------------------------

docker-multiarch-build:
	docker build . -f docker/multiarch_build/Dockerfile.debian \
    --build-arg BUILD_ARCH=armhf \
    --build-arg CPU_ARCH=armv7l \
    --build-arg BUILD_FROM=arm32v7/python:3.6-slim-stretch \
    -t rhasspy/multi-arch/build
