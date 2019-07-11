.PHONY: docker pyinstaller debian

docker:
	docker build . -t rhasspy/intent-recognition/fsticuffs

pyinstaller:
	./build.sh

debian: pyinstaller
	rsync -rv --delete dist/fsticuffs/ debian/rhasspy-fsticuffs_1.0_amd64/usr/lib/rhasspy/fsticuffs/
	cd debian && fakeroot dpkg --build rhasspy-fsticuffs_1.0_amd64
