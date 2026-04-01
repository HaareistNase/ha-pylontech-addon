#!/usr/bin/env python3
import os
import sys
import json
import time
import paho.mqtt.client as mqtt
from pylontech import Pylontech

print("=== Pylontech Reader Starting ===")

# Konfiguration laden - Priorität: options.json > Umgebungsvariablen
try:
    with open('/data/options.json') as f:
        config = json.load(f)
        SERIAL_PORT = config['serial_port']
        BAUDRATE = config['baudrate']
        MQTT_HOST = config['mqtt_host']
        MQTT_TOPIC = config['mqtt_topic']
    print(f"✓ Config loaded from /data/options.json")
except Exception as e:
    print(f"⚠ Could not load /data/options.json: {e}")
    SERIAL_PORT = os.getenv('CONFIG_SERIAL_PORT', '/dev/ttyUSB1')
    BAUDRATE = int(os.getenv('CONFIG_BAUDRATE', '115200'))
    MQTT_HOST = os.getenv('CONFIG_MQTT_HOST', 'core-mosquitto')
    MQTT_TOPIC = os.getenv('CONFIG_MQTT_TOPIC', 'pylontech/battery')
    print(f"✓ Using environment variables")

print(f"Configuration:")
print(f"  Serial Port: {SERIAL_PORT}")
print(f"  Baudrate: {BAUDRATE}")
print(f"  MQTT Host: {MQTT_HOST}")
print(f"  MQTT Topic: {MQTT_TOPIC}")

# Prüfe ob der Port existiert
if not os.path.exists(SERIAL_PORT):
    print(f"❌ ERROR: {SERIAL_PORT} does not exist!")
    import glob
    ports = glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*')
    print(f"Available ports: {ports}")
    sys.exit(1)

# MQTT Client
try:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.connect(MQTT_HOST, 1883, 60)
    print(f"✓ Connected to MQTT broker")
except:
    print(f"⚠ Using deprecated MQTT API")
    client = mqtt.Client()
    client.connect(MQTT_HOST, 1883, 60)

# Pylontech initialisieren
try:
    print(f"Connecting to {SERIAL_PORT}...")
    battery = Pylontech(SERIAL_PORT, baudrate=BAUDRATE)
    print(f"✓ Successfully connected!")
except Exception as e:
    print(f"❌ Failed to connect: {e}")
    sys.exit(1)

print("=== Starting main loop ===")

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
        print(f"Published: SOC={data.soc}%, Voltage={data.voltage}V, Current={data.current}A")
        
    except Exception as e:
        print(f"Error in main loop: {e}")
    
    time.sleep(5)
