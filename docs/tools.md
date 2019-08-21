# Tools

## Wake Word

If you want Rhasspy to always be on and listening, you will need a "wake" word to tell it when to start recording a voice command.

The `rhasspy-porcupine-mqtt` tool listens for a wake word with [porcupine](https://github.com/Picovoice/Porcupine):

```bash
rhasspy-porcupine-mqtt --profile <PROFILE_DIRECTORY>
```

### MQTT Events

Event prefix: `rhasspy/wake-word/`

* Input Events
    * `start-listening`
        * Start processing audio, looking for a wake word
    * `stop-listening`
        * Stop processing audio
    * `reload`
        * Reload keyword(s)
* Output Events
    * `listening-started`
        * Response to `start-listening`
    * `listening-stopped`
        * Response to `stop-listening`
    * `receiving-audio`
        * Sent when first audio chunk is read after listening starts
    * `detected`
        * Wake word has been detected in the audio stream
    * `reloaded`
        * Response to `reload`
    * `error`
        * Unexpected error

### Profile Settings

```yaml
wake-word:
  audio-input:
    host: 127.0.0.1
    port: 12200
  mqtt:
      topic: "rhasspy/wake-word/#"
  porcupine:
    keyword: "/path/to/porcupine.ppn"
    library: "/path/to/libpv_porcupine.so"
    model: "/path/to/porcupine_params.pv"
```

There are a lot of [keyword files](https://github.com/Picovoice/Porcupine/tree/master/resources/keyword_files) available for download. Use the `linux` platform if you're on desktop/laptop (`amd64`) and the `raspberrypi` platform if you're using a Raspberry Pi (`armhf`/`aarch64`).

If you want to create a custom wake word, you will need to run the [Porcupine Optimizer](https://github.com/Picovoice/Porcupine/tree/master/tools/optimizer). **NOTE**: the generated keyword file is only valid for 30 days, though you can always just re-run the optimizer.

### Command Line Tool

`rhasspy-porcupine` takes 16-bit 16Khz mono PCM audio on `stdin` and outputs a JSON event when the wake word is detected.

```bash
gst-launch-1.0 \
    autoaudiosrc ! \
    audioconvert ! \
    audioresample ! \
    audio/x-raw, rate=16000, channels=1, format=S16LE ! \
    filesink location=/dev/stdout | \
rhasspy-porcupine
```

Output:

```json
{"index": 0, "keyword": "/path/to/porcupine.ppn"}
```
