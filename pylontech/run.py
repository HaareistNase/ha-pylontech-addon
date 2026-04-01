#!/usr/bin/env python3
import os
import sys
import json
import time
import glob
import paho.mqtt.client as mqtt
from pylontech import Pylontech

print("\n" + "="*60)
print("PYLONTECH READER - STARTING v2.1")
print("="*60)

# Zeige verfügbare Ports
print("\nAvailable serial ports:")
tty_ports = glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*')
for port in tty_ports:
    print(f"  {port}")

# Lade Konfiguration
try:
    with open('/data/options.json') as f:
        config = json.load(f)
        SERIAL_PORT = config.get('serial_port', '/dev/ttyUSB1')
        BAUDRATE = config.get('baudrate', 115200)
        MQTT_HOST = config.get('mqtt_host', 'core-mosquitto')
        MQTT_TOPIC = config.get('mqtt_topic', 'pylontech/battery')
    print(f"\n✓ Configuration loaded from /data/options.json")
    print(f"  {SERIAL_PORT} @ {BAUDRATE} baud")
except Exception as e:
    SERIAL_PORT = '/dev/ttyUSB1'
    BAUDRATE = 115200
    MQTT_HOST = 'core-mosquitto'
    MQTT_TOPIC = 'pylontech/battery'
    print(f"\n⚠ Using default configuration: {SERIAL_PORT}")

# Prüfe Port
if not os.path.exists(SERIAL_PORT):
    print(f"\n❌ ERROR: {SERIAL_PORT} does not exist!")
    print(f"   Available ports: {tty_ports}")
    sys.exit(1)

print(f"\n✓ Port {SERIAL_PORT} exists")

# MQTT Verbindung
print(f"\nConnecting to MQTT broker at {MQTT_HOST}...")
try:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.connect(MQTT_HOST, 1883, 60)
    print(f"✓ Connected to MQTT")
except:
    client = mqtt.Client()
    client.connect(MQTT_HOST, 1883, 60)
    print(f"✓ Connected to MQTT (legacy mode)")

# Pylontech Verbindung
print(f"\nConnecting to Pylontech battery on {SERIAL_PORT}...")
try:
    battery = Pylontech(SERIAL_PORT, baudrate=BAUDRATE)
    print(f"✓ Connected to Pylontech battery!")
except Exception as e:
    print(f"❌ Failed to connect: {e}")
    print(f"\nTroubleshooting:")
    print(f"  - Check if the battery is powered on")
    print(f"  - Verify the USB cable is connected")
    print(f"  - Try a different baudrate (9600, 19200, 115200)")
    sys.exit(1)

print("\n" + "="*60)
print("STARTING MAIN LOOP - Publishing to MQTT")
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
        print(f"[{time.strftime('%H:%M:%S')}] SOC: {data.soc}% | {data.voltage:.1f}V | {data.current:.1f}A | {data.voltage * data.current:.0f}W")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    time.sleep(5)
