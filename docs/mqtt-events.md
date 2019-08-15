# Rhasspy MQTT Events

## Topic Patterns

Rhasspy's MQTT event topics generally follow a pattern:

```
rhasspy/<service-category>/<event-name>/[<optional>]
```

For example, the `pocketsphinx` speech to text service has a `start-listening` event whose MQTT topic is:

```
rhasspy/speech-to-text/start-listening
```

Many services support adding an `<optional>` component to the end of the MQTT topic, for example:

```
rhasspy/speech-to-text/start-listening/living-room
```

You can now adjust the `mqtt-topic` of any service to be something like:

```
rhasspy/speech-to-text/+/living-room
```

in order to isolate multiple instances of Rhasspy on the same MQTT broker.

## Event Paylods

All Rhasspy events expect a JSON object as a payload. The object properties will be different for every event.

## Wake Word

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

## Voice Command

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

## Speech to Text

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

## Intent Recognition

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

## Text to Speech

Event prefix: `rhasspy/text-to-speech/`

* Input Events
    * `say-text`
        * Generate an audio file with spoken text and send a `rhasspy/audio-output/play-uri` event with its URI
        * `text` - text to speak
* Output Events
    * `text-said`
        * Response to `say-text`

## Audio Output

Event prefix: `rhasspy/audio-output/`

* Input Events
    * `play-uri`
        * Play a media file URI through the speakers
        * `uri` - URI of media file to play
* Output Events
    * `uri-played`
        * Response sent after media item has finished playing
        * `uri` - URI of media file that was played

## Training

Event prefix: `rhasspy/training/`

* Input Events
    * `start-training`
        * Ask Rhasspy to re-train speech/intent models
* Output Events
    * `training-started`
        * Response to `start-training`
    * `training-completed`
        * Response sent when training was successful
    * `error`
        * Unexpected error
