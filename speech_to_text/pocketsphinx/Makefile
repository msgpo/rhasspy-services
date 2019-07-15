.PHONY: docker pyinstaller debian

docker:
	docker build . -t rhasspy/speech-to-text/pocketsphinx

pyinstaller:
	./build.sh

debian: pyinstaller
	rsync -rv --delete dist/pocketsphinx_rhasspy/ debian/rhasspy-pocketsphinx_1.0_amd64/usr/lib/rhasspy/pocketsphinx/
	cd debian && fakeroot dpkg --build rhasspy-pocketsphinx_1.0_amd64
