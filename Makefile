.PHONY: debian-fsticuffs \
        docker-espeak \
        docker-fsticuffs \
        docker-pocketsphinx \
        docker-porcupine \
        docker-pulseaudio-input \
        docker-pulseaudio-output \
        docker-webrtcvad \
        installer-fsticuffs

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

# -----------------------------------------------------------------------------
# Debian
# -----------------------------------------------------------------------------

debian-fsticuffs: installer-fsticuffs
	bash debianize.sh intent_recognition fsticuffs $(FRIENDLY_ARCH)
