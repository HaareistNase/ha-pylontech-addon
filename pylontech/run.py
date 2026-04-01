#!/usr/bin/env python3
import os
import sys
import json
import time
import paho.mqtt.client as mqtt
from pylontech import Pylontech

print("=" * 60)
print("PYLONTECH BATTERY READER v4.0")
print("=" * 60)

# Konfiguration laden
try:
    with open('/data/options.json') as f:
        config = json.load(f)
        SERIAL_PORT = config['serial_port']
        BAUDRATE = config['baudrate']
        MQTT_HOST = config['mqtt_host']
        MQTT_TOPIC = config['mqtt_topic']
    print(f"✓ Config loaded: {SERIAL_PORT} @ {BAUDRATE} baud")
except Exception as e:
    print(f"✗ Config load failed: {e}")
    sys.exit(1)

print(f"  MQTT: {MQTT_HOST}")
print(f"  Topic: {MQTT_TOPIC}")

# Prüfe Port
if not os.path.exists(SERIAL_PORT):
    print(f"\n✗ ERROR: {SERIAL_PORT} does not exist!")
    import glob
    ports = glob.glob('/dev/ttyUSB*')
    print(f"  Available: {ports}")
    sys.exit(1)

print(f"\n✓ Port {SERIAL_PORT} found")

# MQTT
print("\nConnecting to MQTT...")
try:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.connect(MQTT_HOST, 1883, 60)
    print(f"✓ Connected")
except:
    client = mqtt.Client()
    client.connect(MQTT_HOST, 1883, 60)
    print(f"✓ Connected (legacy)")

# Pylontech - DIREKT MIT STRING, NICHT MIT SERIAL OBJEKT!
print(f"\nConnecting to battery on {SERIAL_PORT}...")
try:
    battery = Pylontech(SERIAL_PORT, baudrate=BAUDRATE)
    print(f"✓ Connected to Pylontech battery!")
except Exception as e:
    print(f"✗ Connection failed: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("STARTING - Publishing to MQTT every 5 seconds")
print("=" * 60 + "\n")

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
        print(f"[{time.strftime('%H:%M:%S')}] SOC: {data.soc}% | {data.voltage:.2f}V | {data.current:.2f}A | Power: {data.voltage * data.current:.1f}W")
        
    except Exception as e:
        print(f"✗ Error: {e}")
    
    time.sleep(5)
