[
  {
    "id": "e875cee2.7f4d6",
    "type": "tab",
    "label": "Flow 1",
    "disabled": false,
    "info": ""
  },
  {
    "id": "fd5d23bc.65b79",
    "type": "mqtt in",
    "z": "e875cee2.7f4d6",
    "name": "",
    "topic": "rhasspy/wake-word/detected",
    "qos": "2",
    "datatype": "auto",
    "broker": "d09fceb.acd66b",
    "x": 190,
    "y": 100,
    "wires": [
      [
        "7e1dc5af.7cef0c",
        "6bbf07c.fe5a7f8",
        "e47ba5de.d61b4"
      ]
    ]
  },
  {
    "id": "6bbf07c.fe5a7f8",
    "type": "mqtt out",
    "z": "e875cee2.7f4d6",
    "name": "",
    "topic": "rhasspy/voice-command/start-listening",
    "qos": "",
    "retain": "",
    "broker": "d09fceb.acd66b",
    "x": 290,
    "y": 300,
    "wires": []
  },
  {
    "id": "7e1dc5af.7cef0c",
    "type": "mqtt out",
    "z": "e875cee2.7f4d6",
    "name": "",
    "topic": "rhasspy/wake-word/stop-listening",
    "qos": "",
    "retain": "",
    "broker": "d09fceb.acd66b",
    "x": 270,
    "y": 220,
    "wires": []
  },
  {
    "id": "e7baa958.fe533",
    "type": "mqtt in",
    "z": "e875cee2.7f4d6",
    "name": "",
    "topic": "rhasspy/voice-command/command-stopped",
    "qos": "2",
    "datatype": "auto",
    "broker": "d09fceb.acd66b",
    "x": 220,
    "y": 580,
    "wires": [
      [
        "749033fd.65178c",
        "9ce68078.348cb8"
      ]
    ]
  },
  {
    "id": "749033fd.65178c",
    "type": "mqtt out",
    "z": "e875cee2.7f4d6",
    "name": "",
    "topic": "rhasspy/speech-to-text/stop-listening",
    "qos": "",
    "retain": "",
    "broker": "d09fceb.acd66b",
    "x": 242,
    "y": 660,
    "wires": []
  },
  {
    "id": "2f72c4d0.9e94ec",
    "type": "debug",
    "z": "e875cee2.7f4d6",
    "name": "",
    "active": true,
    "tosidebar": true,
    "console": false,
    "tostatus": false,
    "complete": "false",
    "x": 190,
    "y": 1080,
    "wires": []
  },
  {
    "id": "e84e9d98.1b1448",
    "type": "mqtt in",
    "z": "e875cee2.7f4d6",
    "name": "",
    "topic": "rhasspy/speech-to-text/text-captured",
    "qos": "2",
    "datatype": "auto",
    "broker": "d09fceb.acd66b",
    "x": 170,
    "y": 880,
    "wires": [
      [
        "2f72c4d0.9e94ec",
        "73f4b204.f871c4"
      ]
    ]
  },
  {
    "id": "e47ba5de.d61b4",
    "type": "mqtt out",
    "z": "e875cee2.7f4d6",
    "name": "",
    "topic": "rhasspy/speech-to-text/start-listening",
    "qos": "",
    "retain": "",
    "broker": "d09fceb.acd66b",
    "x": 280,
    "y": 380,
    "wires": []
  },
  {
    "id": "9ce68078.348cb8",
    "type": "mqtt out",
    "z": "e875cee2.7f4d6",
    "name": "",
    "topic": "rhasspy/wake-word/start-listening",
    "qos": "",
    "retain": "",
    "broker": "d09fceb.acd66b",
    "x": 230,
    "y": 740,
    "wires": []
  },
  {
    "id": "73f4b204.f871c4",
    "type": "mqtt out",
    "z": "e875cee2.7f4d6",
    "name": "",
    "topic": "rhasspy/intent-recognition/recognize-intent",
    "qos": "",
    "retain": "",
    "broker": "d09fceb.acd66b",
    "x": 250,
    "y": 980,
    "wires": []
  },
  {
    "id": "fac6e398.502f9",
    "type": "mqtt in",
    "z": "e875cee2.7f4d6",
    "name": "",
    "topic": "rhasspy/intent-recognition/intent-recognized",
    "qos": "2",
    "datatype": "auto",
    "broker": "d09fceb.acd66b",
    "x": 210,
    "y": 1200,
    "wires": [
      [
        "77db5fde.320998"
      ]
    ]
  },
  {
    "id": "77db5fde.320998",
    "type": "debug",
    "z": "e875cee2.7f4d6",
    "name": "",
    "active": true,
    "tosidebar": true,
    "console": false,
    "tostatus": false,
    "complete": "false",
    "x": 190,
    "y": 1280,
    "wires": []
  },
  {
    "id": "d09fceb.acd66b",
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
