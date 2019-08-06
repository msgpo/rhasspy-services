.PHONY: debian-fsticuffs \
        debian-train \
        docker-espeak \
        docker-fsticuffs \
        docker-pocketsphinx \
        docker-porcupine \
        docker-pulseaudio-input \
        docker-pulseaudio-output \
        docker-webrtcvad \
        installer-fsticuffs \
        installer-train

# -----------------------------------------------------------------------------

FRIENDLY_ARCH ?= amd64

# -----------------------------------------------------------------------------
# Docker
# -----------------------------------------------------------------------------

docker-espeak:
	docker build . -f docker/text_to_speech/espeak/Dockerfile -t rhasspy/text-to-speech/espeak

docker-fsticuffs:
	docker build . -f docker/intent_recognition/fsticuffs/Dockerfile -t rhasspy/intent-recognition/fsticuffs

docker-pocketsphinx:
	docker build . -f docker/speech_to_text/pocketsphinx/Dockerfile -t rhasspy/speech-to-text/pocketsphinx

docker-porcupine:
	docker build . -f docker/wake_word/porcupine/Dockerfile -t rhasspy/wake-word/porcupine

docker-pulseaudio-input:
	docker build . -f docker/audio_input/pulseaudio/Dockerfile -t rhasspy/audio-input/pulseaudio

docker-pulseaudio-output:
	docker build . -f docker/audio_output/pulseaudio/Dockerfile -t rhasspy/audio-output/pulseaudio

docker-webrtcvad:
	docker build . -f docker/voice_command/webrtcvad//Dockerfile -t rhasspy/voice-command/webrtcvad

# -----------------------------------------------------------------------------
# PyInstaller
# -----------------------------------------------------------------------------

installer-fsticuffs:
	bash build.sh installer/intent_recognition/fsticuffs.spec

installer-train:
	bash build.sh installer/training/ini_jsgf.spec
	bash build.sh installer/training/vocab_g2p.spec
	bash build.sh installer/training/vocab_dict.spec
	bash build.sh installer/training/jsgf_fst_arpa.spec
	bash build.sh installer/training/train.spec

# -----------------------------------------------------------------------------
# Debian
# -----------------------------------------------------------------------------

debian-fsticuffs: installer-fsticuffs
	bash debianize.sh intent_recognition fsticuffs $(FRIENDLY_ARCH)

debian-train: installer-train
	rsync -av dist/ini_jsgf/ dist/vocab_g2p/ dist/vocab_dict/ dist/jsgf_fst_arpa/ dist/train/
	bash debianize.sh training train $(FRIENDLY_ARCH)
