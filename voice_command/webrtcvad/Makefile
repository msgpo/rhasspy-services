.PHONY: docker pyinstaller debian

docker:
	docker build . -t rhasspy/voice-detection/webrtcvad

pyinstaller:
	./build.sh

debian: pyinstaller
	rsync -rv --delete dist/webrtcvad_rhasspy/ debian/rhasspy-webrtcvad_1.0_amd64/usr/lib/rhasspy/webrtcvad/
	cd debian && fakeroot dpkg --build rhasspy-webrtcvad_1.0_amd64
