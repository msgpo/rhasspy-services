docker-pocketsphinx:
	docker build . -f docker/speech_to_text/pocketsphinx/Dockerfile -t rhasspy/speech-to-text/pocketsphinx
