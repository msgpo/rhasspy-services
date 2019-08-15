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

## Speech to Text

Event prefix: `rhasspy/speech-to-text/`

* Input Events
    * `start-listening`
    * `stop-listening`
    * `reload`
* Output Events
    * `listening-started`
    * `receiving-audio`
    * `listening-stopped`
    * `text-captured`
    * `reloaded`
    * `error`


## Intent Recognition

Event prefix: `rhasspy/intent-recognition`

* Input Events
    * `recognize-intent`
    * `reload`
* Output Events
    * `intent-recognized`
    * `reloaded`
    * `error`
