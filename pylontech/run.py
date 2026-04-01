#!/usr/bin/env python3
import os
import sys
import json
import time
import paho.mqtt.client as mqtt
from pylontech import Pylontech

# HARDCODED - direkt den richtigen Port verwenden
SERIAL_PORT = "/dev/ttyUSB1"
BAUDRATE = 115200
MQTT_HOST = "core-mosquitto"
MQTT_TOPIC = "pylontech/battery"

print("=== PYLONTECH READER ===")
print(f"Using PORT: {SERIAL_PORT}")
print(f"Baudrate: {BAUDRATE}")

# Prüfe ob der Port existiert
if os.path.exists(SERIAL_PORT):
    print(f"✓ {SERIAL_PORT} exists")
else:
    print(f"❌ {SERIAL_PORT} does NOT exist!")
    # Zeige verfügbare Ports
    import glob
    ports = glob.glob('/dev/ttyUSB*')
    print(f"Available ports: {ports}")

# MQTT
client = mqtt.Client()
client.connect(MQTT_HOST, 1883, 60)
print(f"✓ Connected to MQTT")

# Pylontech
print(f"Connecting to battery...")
battery = Pylontech(SERIAL_PORT, baudrate=BAUDRATE)
print(f"✓ Connected!")

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
        }
        client.publish(MQTT_TOPIC, json.dumps(payload), retain=True)
        print(f"SOC: {data.soc}% | {data.voltage}V | {data.current}A")
    except Exception as e:
        print(f"Error: {e}")
    time.sleep(5)
