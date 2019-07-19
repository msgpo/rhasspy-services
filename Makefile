docker-pocketsphinx:
	docker build . -f docker/speech_to_text/pocketsphinx/Dockerfile -t rhasspy/speech-to-text/pocketsphinx

docker-pulseaudio-output:
	docker build . -f docker/audio_output/pulseaudio/Dockerfile -t rhasspy/audio-output/pulseaudio

docker-espeak:
	docker build . -f docker/text_to_speech/espeak/Dockerfile -t rhasspy/text-to-speech/espeak
