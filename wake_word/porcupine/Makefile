.PHONY: docker pyinstaller debian

docker:
	docker build . -t rhasspy/wake-word/porcupine

pyinstaller:
	./build.sh

debian: pyinstaller
	rsync -rv --delete dist/porcupine_rhasspy/ debian/rhasspy-porcupine_1.0_amd64/usr/lib/rhasspy/porcupine/
	cd debian && fakeroot dpkg --build rhasspy-porcupine_1.0_amd64
