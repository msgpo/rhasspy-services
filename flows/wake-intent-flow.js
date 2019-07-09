[
  {
    "id": "dfd1fbde.17871",
    "type": "tab",
    "label": "Flow 1",
    "disabled": false,
    "info": ""
  },
  {
    "id": "a99c30f4.c7f4e8",
    "type": "mqtt in",
    "z": "dfd1fbde.17871",
    "name": "",
    "topic": "rhasspy/wake-word/detected",
    "qos": "2",
    "datatype": "auto",
    "broker": "63b50e48.89dbb",
    "x": 190,
    "y": 100,
    "wires": [
      [
        "1bbbdc30.2a66e4",
        "68481dec.868e6c",
        "a507e388.18edf8"
      ]
    ]
  },
  {
    "id": "68481dec.868e6c",
    "type": "mqtt out",
    "z": "dfd1fbde.17871",
    "name": "",
    "topic": "rhasspy/voice-command/start-listening",
    "qos": "",
    "retain": "",
    "broker": "63b50e48.89dbb",
    "x": 290,
    "y": 300,
    "wires": []
  },
  {
    "id": "1bbbdc30.2a66e4",
    "type": "mqtt out",
    "z": "dfd1fbde.17871",
    "name": "",
    "topic": "rhasspy/wake-word/stop-listening",
    "qos": "",
    "retain": "",
    "broker": "63b50e48.89dbb",
    "x": 270,
    "y": 220,
    "wires": []
  },
  {
    "id": "a7a95b2a.e3e07",
    "type": "mqtt in",
    "z": "dfd1fbde.17871",
    "name": "",
    "topic": "rhasspy/voice-command/command-stopped",
    "qos": "2",
    "datatype": "auto",
    "broker": "63b50e48.89dbb",
    "x": 220,
    "y": 520,
    "wires": [
      [
        "80e37049.27316",
        "8edb44f5.e0705"
      ]
    ]
  },
  {
    "id": "80e37049.27316",
    "type": "mqtt out",
    "z": "dfd1fbde.17871",
    "name": "",
    "topic": "rhasspy/speech-to-text/stop-listening",
    "qos": "",
    "retain": "",
    "broker": "63b50e48.89dbb",
    "x": 242,
    "y": 600,
    "wires": []
  },
  {
    "id": "4da7cfa7.09a9f8",
    "type": "debug",
    "z": "dfd1fbde.17871",
    "name": "",
    "active": true,
    "tosidebar": true,
    "console": false,
    "tostatus": false,
    "complete": "false",
    "x": 450,
    "y": 820,
    "wires": []
  },
  {
    "id": "e6eb091d.c2fc58",
    "type": "mqtt in",
    "z": "dfd1fbde.17871",
    "name": "",
    "topic": "rhasspy/speech-to-text/text-captured",
    "qos": "2",
    "datatype": "auto",
    "broker": "63b50e48.89dbb",
    "x": 170,
    "y": 820,
    "wires": [
      [
        "4da7cfa7.09a9f8",
        "1be24562.6df8d3"
      ]
    ]
  },
  {
    "id": "a507e388.18edf8",
    "type": "mqtt out",
    "z": "dfd1fbde.17871",
    "name": "",
    "topic": "rhasspy/speech-to-text/start-listening",
    "qos": "",
    "retain": "",
    "broker": "63b50e48.89dbb",
    "x": 280,
    "y": 380,
    "wires": []
  },
  {
    "id": "8edb44f5.e0705",
    "type": "mqtt out",
    "z": "dfd1fbde.17871",
    "name": "",
    "topic": "rhasspy/wake-word/start-listening",
    "qos": "",
    "retain": "",
    "broker": "63b50e48.89dbb",
    "x": 230,
    "y": 680,
    "wires": []
  },
  {
    "id": "1be24562.6df8d3",
    "type": "mqtt out",
    "z": "dfd1fbde.17871",
    "name": "",
    "topic": "rhasspy/intent-recognition/recognize-intent",
    "qos": "",
    "retain": "",
    "broker": "63b50e48.89dbb",
    "x": 250,
    "y": 920,
    "wires": []
  },
  {
    "id": "54cffc01.2a3fd4",
    "type": "mqtt in",
    "z": "dfd1fbde.17871",
    "name": "",
    "topic": "rhasspy/intent-recognition/intent-recognized",
    "qos": "2",
    "datatype": "auto",
    "broker": "63b50e48.89dbb",
    "x": 200,
    "y": 1080,
    "wires": [
      [
        "ca51b003.461b18",
        "a72a8a39.4cecd8"
      ]
    ]
  },
  {
    "id": "ca51b003.461b18",
    "type": "debug",
    "z": "dfd1fbde.17871",
    "name": "",
    "active": true,
    "tosidebar": true,
    "console": false,
    "tostatus": false,
    "complete": "false",
    "x": 480,
    "y": 1080,
    "wires": []
  },
  {
    "id": "a72a8a39.4cecd8",
    "type": "mqtt out",
    "z": "dfd1fbde.17871",
    "name": "",
    "topic": "rhasspy/text-to-speech/say-text",
    "qos": "",
    "retain": "",
    "broker": "63b50e48.89dbb",
    "x": 210,
    "y": 1180,
    "wires": []
  },
  {
    "id": "63b50e48.89dbb",
    "type": "mqtt-broker",
    "z": "",
    "name": "default",
    "broker": "localhost",
    "port": "1883",
    "clientid": "",
    "usetls": false,
    "compatmode": true,
    "keepalive": "60",
    "cleansession": true,
    "birthTopic": "",
    "birthQos": "0",
    "birthPayload": "",
    "closeTopic": "",
    "closeQos": "0",
    "closePayload": "",
    "willTopic": "",
    "willQos": "0",
    "willPayload": ""
  }
]
