#!/usr/bin/env python3
import os
import sys
import json
import time
import glob
import paho.mqtt.client as mqtt
from pylontech import Pylontech

print("\n" + "="*60)
print("PYLONTECH READER - STARTING")
print("="*60)

# Zeige verfügbare Ports
print("\nAvailable serial ports:")
for port in glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*'):
    print(f"  {port}")

# Lade Konfiguration
try:
    with open('/data/options.json') as f:
        config = json.load(f)
        SERIAL_PORT = config.get('serial_port', '/dev/ttyUSB1')
        BAUDRATE = config.get('baudrate', 115200)
        MQTT_HOST = config.get('mqtt_host', 'core-mosquitto')
        MQTT_TOPIC = config.get('mqtt_topic', 'pylontech/battery')
    print(f"\nConfiguration loaded from /data/options.json")
except:
    SERIAL_PORT = '/dev/ttyUSB1'
    BAUDRATE = 115200
    MQTT_HOST = 'core-mosquitto'
    MQTT_TOPIC = 'pylontech/battery'
    print(f"\nUsing default configuration")

print(f"\nConfiguration:")
print(f"  Serial Port: {SERIAL_PORT}")
print(f"  Baudrate: {BAUDRATE}")
print(f"  MQTT Host: {MQTT_HOST}")
print(f"  MQTT Topic: {MQTT_TOPIC}")

# Prüfe Port
if not os.path.exists(SERIAL_PORT):
    print(f"\n❌ ERROR: {SERIAL_PORT} does not exist!")
    sys.exit(1)

# MQTT Verbindung
print(f"\nConnecting to MQTT...")
try:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.connect(MQTT_HOST, 1883, 60)
    print(f"✓ Connected to {MQTT_HOST}")
except:
    client = mqtt.Client()
    client.connect(MQTT_HOST, 1883, 60)
    print(f"✓ Connected (legacy mode)")

# Pylontech Verbindung
print(f"\nConnecting to Pylontech on {SERIAL_PORT}...")
try:
    battery = Pylontech(SERIAL_PORT, baudrate=BAUDRATE)
    print(f"✓ Connected successfully!")
except Exception as e:
    print(f"❌ Failed: {e}")
    sys.exit(1)

print("\n" + "="*60)
print("STARTING MAIN LOOP")
print("="*60 + "\n")

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
        print(f"[{time.strftime('%H:%M:%S')}] SOC: {data.soc}% | {data.voltage}V | {data.current}A")
    except Exception as e:
        print(f"Error: {e}")
    time.sleep(5)
