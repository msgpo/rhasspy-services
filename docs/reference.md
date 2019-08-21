# Reference

## Tools

* Wake Word
    * `rhasspy-porcupine`
        * Input: 16-bit 16Khz mono PCM audio
        * Output: JSON object when wake word is recognized
    * `rhasspy-porcupine-mqtt`
        * [MQTT Events](#wake-word)
* Voice Command
    * `rhasspy-webrtcvad`
        * Input: 16-bit 16Khz mono PCM audio
        * Output: Event name + JSON object when voice command starts/stops
    * `rhasspy-webrtcvad-mqtt`
        * [MQTT Events](#voice-command)
* Speech to Text
    * `rhasspy-pocketsphinx`
        * Input: 16-bit 16Khz mono PCM audio
        * Output: JSON object with transcription text
    * `rhasspy-pocketsphinx-mqtt`
        * [MQTT Events](#speech-to-text)
    * `rhasspy-kaldi`
        * Input: 16-bit 16Khz mono PCM audio
        * Output: JSON object with transcription text
    * `rhasspy-kaldi-mqtt`
        * [MQTT Events](#speech-to-text)
* Intent Recognition
    * `rhasspy-fsticuffs`
        * Input: JSON object with text to recognize
        * Output: JSON object with recognized intent
    * `rhasspy-fsticuffs-mqtt`
        * [MQTT Events](#intent-recognition)
* Text to Speech
    * `rhasspy-espeak`
    * `rhasspy-espeak-mqtt`
        * [MQTT Events](#text-to-speech)
* Training
    * `rhasspy-train`
        * Input: Profile directory, sentences.ini
        * Output: Custom speech + intent models
    * `rhasspy-train-mqtt`
        * [MQTT Events](#training)
    * `rhasspy-kaldi-train`
* Audio Input
    * `rhasspy-pulseaudio-input`
        * Input: Microphone audio
        * Output: 16-bit 16Khz mono PCM audio stream over UDP
* Audio Output
    * `rhasspy-pulseaudio-output-mqtt`
        * [MQTT Events](#audio-output)

## MQTT Events

### Wake Word

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

### Voice Command

Event prefix: `rhasspy/voice-command/`

* Input Events
    * `start-listening`
        * Start processing audio, looking for voice commands
* Output Events
    * `listening-started`
        * Response to `start-listening`
    * `receiving-audio`
        * Sent when first audio chunk is read after listening starts
    * `speech`
        * Speech detected in chunk
    * `silence`
        * Speech detected in chunk (after speech)
    * `command-started`
        * Voice command has started
    * `command-stopped`
        * Voice command has finished
    * `command-timeout`
        * Voice command was not found or did not finish before timeout
    * `error`
        * Unexpected error

### Speech to Text

Event prefix: `rhasspy/speech-to-text/`

* Input Events
    * `start-listening`
        * Start buffering audio
    * `stop-listening`
        * Stop buffering audio, transcribe buffered audio
    * `reload`
        * Reload speech model
* Output Events
    * `listening-started`
        * Response to `start-listening`
    * `listening-stopped`
        * Response to `stop-listening`
    * `receiving-audio`
        * Sent when first audio chunk is read after listening starts
    * `text-captured`
        * Results of transcription
        * `text` - transcribed text
    * `reloaded`
        * Response to `reload`
    * `error`
        * Unexpected error

### Intent Recognition

Event prefix: `rhasspy/intent-recognition/`

* Input Events
    * `recognize-intent`
        * Request to recognize intent from text
        * `text` - text to process
    * `reload`
        * Reload intent model
* Output Events
    * `intent-recognized`
        * Intent recognized in response to `recognize-intent` request
        * `intent` - recognized intent
    * `reloaded`
        * Response to `reload`
    * `error`
        * Unexpected error

### Text to Speech

Event prefix: `rhasspy/text-to-speech/`

* Input Events
    * `say-text`
        * Generate an audio file with spoken text and send a `rhasspy/audio-output/play-uri` event with its URI
        * `text` - text to speak
    * `pronounce-phonemes`
        * Generate an audio file with a pronunciation of the given phonemes and send a `rhasspy/audio-output/play-uri` event with its URI
        * `phonemes` - phonemes to speak, separated by spaces
* Output Events
    * `text-said`
        * Response to `say-text`
    * `phonemes-pronounced`
        * Response to `pronounce-phonemes`

### Audio Output

Event prefix: `rhasspy/audio-output/`

* Input Events
    * `play-uri`
        * Play a media file URI through the speakers
        * `uri` - URI of media file to play
* Output Events
    * `uri-played`
        * Response sent after media item has finished playing
        * `uri` - URI of media file that was played

### Training

Event prefix: `rhasspy/training/`

* Input Events
    * `start-training`
        * Ask Rhasspy to re-train speech/intent models
* Output Events
    * `training-started`
        * Response to `start-training`
    * `training-completed`
        * Response sent when training was successful
    * `training-failed`
        * Response sent when training was **not** successful
    * `error`
        * Unexpected error

## Profile Settings

Rhasspy expects a `profile.yml` file in your profile directory.

You can use the custom `!env` tag to expand environment variables, such as:

* `${profile_dir}` - path to your profile directory
* `${rhasspy_dir}` - path to the directory where Rhasspy is installed

Example:

```yaml
some_setting: !env "${profile_dir}/file_in_profile"
```

### Available Settings

```yaml
# Audio input from a microphone.
# Streamed via UDP to multiple services.
audio-input:
  pulseaudio:
    # List of HOST:PORT UDP clients
    clients:
      - 127.0.0.1:12200
      - 127.0.0.1:12201
      - 127.0.0.1:12202

# Listens for "wake" word to start recording a voice command
wake-word:
  # UDP host/port for 16-bit 16Khz mono PCM audio
  audio-input:
    host: 127.0.0.1
    port: 12200
  mqtt:
      topic: "rhasspy/wake-word/#"
  # Default wake word system
  porcupine:
    keyword: "/path/to/porcupine.ppn"
    library: "/path/to/libpv_porcupine.so"
    model: "/path/to/porcupine_params.pv"

# Determines when a voice command has finished
voice-command:
  # UDP host/port for 16-bit 16Khz mono PCM audio
  audio-input:
    host: 127.0.0.1
    port: 12201

# Transcribes audio data into text
speech-to-text:
  # UDP host/port for 16-bit 16Khz mono PCM audio
  audio-input:
    host: 127.0.0.1
    port: 12202
  pocketsphinx:
    acoustic-model: !env "${rhasspy_dir}/languages/english/en-us_pocketsphinx-cmu/acoustic_model"
    language-model: !env "${profile_dir}/language_model.txt"
    dictionary: !env "${profile_dir}/dictionary.txt"

# Transforms text into JSON events
intent-recognition:
  # Default intent recognizer
  fsticuffs:
    # Path to finite state transducer generated during training
    intent-fst: !env "${profile_dir}/intent.fst"
    
    # True if unknown words should be ignored
    skip-unknown: true
    
    # True if recognition should be less strict
    fuzzy: true

text-to-speech:
  espeak:
    # Voice used by eSpeak
    voice: en-us
  cache:
    # Directory to cache WAV files generated by eSpeak
    cache-directory: !env "${profile_dir}/tts-cache"

training:
  sentences-file: !env "${profile_dir}/sentences.ini"
  intent-fst: !env "${profile_dir}/intent.fst"
  language-model: !env "${profile_dir}/language_model.txt"
  dictionary: !env "${profile_dir}/dictionary.txt"
  base-dictionary: !env "${rhasspy_dir}/languages/english/en-us_pocketsphinx-cmu/base_dictionary.txt"
  grapheme-to-phoneme-model: !env "${rhasspy_dir}/languages/english/en-us_pocketsphinx-cmu/g2p.fst"
```
