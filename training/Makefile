.PHONY: docker pyinstaller debian

docker:
	docker build . -t rhasspy/training

pyinstaller:
	./build.sh

debian: pyinstaller
	rsync -rv --delete dist/rhasspy_training/ debian/rhasspy-training_1.0_amd64/usr/lib/rhasspy/training/
	cd debian && fakeroot dpkg --build rhasspy-training_1.0_amd64
