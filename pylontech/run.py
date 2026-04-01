#!/usr/bin/env python3
import os
import sys
import json
import time
import paho.mqtt.client as mqtt
from pylontech import Pylontech

# Debug: Zeige alle CONFIG Variablen
print("=== STARTUP DEBUG ===")
print("All CONFIG_* env vars:")
for key in sorted(os.environ.keys()):
    if key.startswith('CONFIG_'):
        print(f"  {key}={os.environ[key]}")

# Konfiguration laden
try:
    with open('/data/options.json') as f:
        config = json.load(f)
        SERIAL_PORT = config['serial_port']
        BAUDRATE = config['baudrate']
        MQTT_HOST = config['mqtt_host']
        MQTT_TOPIC = config['mqtt_topic']
    print(f"Loaded from options.json: {SERIAL_PORT}")
except:
    SERIAL_PORT = os.getenv('CONFIG_SERIAL_PORT', '/dev/ttyUSB1')
    BAUDRATE = int(os.getenv('CONFIG_BAUDRATE', '115200'))
    MQTT_HOST = os.getenv('CONFIG_MQTT_HOST', 'core-mosquitto')
    MQTT_TOPIC = os.getenv('CONFIG_MQTT_TOPIC', 'pylontech/battery')
    print(f"Loaded from env: {SERIAL_PORT}")

print(f"Using SERIAL_PORT: {SERIAL_PORT}")
print(f"BAUDRATE: {BAUDRATE}")
print("====================")

# MQTT Client
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect(MQTT_HOST, 1883, 60)

# Pylontech - WICHTIG: direkt mit dem String, nicht mit einem Serial Objekt
try:
    print(f"Opening {SERIAL_PORT}...")
    battery = Pylontech(SERIAL_PORT, baudrate=BAUDRATE)
    print("Connected successfully!")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)

# Hauptloop
while True:
    try:
        data = battery.get_values()
        payload = {
            "soc": data.soc,
            "voltage": data.voltage,
            "current": data.current,
            "power": data.voltage * data.current,
            "temperature": data.temperature,
            "capacity": getattr(data, "capacity", None)
        }
        client.publish(MQTT_TOPIC, json.dumps(payload), retain=True)
        print(f"Published: {payload}")
    except Exception as e:
        print(f"Error: {e}")
    time.sleep(5)
