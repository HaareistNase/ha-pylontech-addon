#!/usr/bin/env python3
import os
import sys
import json
import time
import glob
import paho.mqtt.client as mqtt
from pylontech import Pylontech

print("\n" + "="*60)
print("PYLONTECH READER - DIAGNOSTIC MODE")
print("="*60)

# 1. Zeige alle verfügbaren seriellen Ports
print("\n1. Available serial ports:")
tty_ports = glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*') + glob.glob('/dev/serial/by-id/*')
for port in tty_ports:
    print(f"   {port}")

# 2. Lade Konfiguration
print("\n2. Loading configuration...")

# Versuche zuerst /data/options.json (Standard für Home Assistant Add-ons)
config = {}
try:
    with open('/data/options.json') as f:
        config = json.load(f)
    print(f"   ✓ Loaded from /data/options.json")
    print(f"   Config: {json.dumps(config, indent=2)}")
except FileNotFoundError:
    print(f"   ⚠ /data/options.json not found")
except Exception as e:
    print(f"   ⚠ Error loading /data/options.json: {e}")

# 3. Hole die Konfiguration mit Fallbacks
SERIAL_PORT = config.get('serial_port') or os.getenv('CONFIG_SERIAL_PORT') or os.getenv('SERIAL_PORT') or '/dev/ttyUSB1'
BAUDRATE = int(config.get('baudrate') or os.getenv('CONFIG_BAUDRATE') or os.getenv('BAUDRATE') or 115200)
MQTT_HOST = config.get('mqtt_host') or os.getenv('CONFIG_MQTT_HOST') or os.getenv('MQTT_HOST') or 'core-mosquitto'
MQTT_TOPIC = config.get('mqtt_topic') or os.getenv('CONFIG_MQTT_TOPIC') or os.getenv('MQTT_TOPIC') or 'pylontech/battery'

print(f"\n3. Final Configuration:")
print(f"   SERIAL_PORT: {SERIAL_PORT}")
print(f"   BAUDRATE: {BAUDRATE}")
print(f"   MQTT_HOST: {MQTT_HOST}")
print(f"   MQTT_TOPIC: {MQTT_TOPIC}")

# 4. Prüfe ob der Port existiert
print(f"\n4. Checking if {SERIAL_PORT} exists...")
if not os.path.exists(SERIAL_PORT):
    print(f"   ❌ ERROR: {SERIAL_PORT} does NOT exist!")
    print(f"   Available ports: {tty_ports}")
    sys.exit(1)
else:
    print(f"   ✓ Port exists")

# 5. Prüfe Berechtigungen
print(f"\n5. Checking permissions...")
try:
    import stat
    st = os.stat(SERIAL_PORT)
    print(f"   Permissions: {oct(st.st_mode)}")
    print(f"   Owner: {st.st_uid}, Group: {st.st_gid}")
    print(f"   Readable: {os.access(SERIAL_PORT, os.R_OK)}")
    print(f"   Writable: {os.access(SERIAL_PORT, os.W_OK)}")
except Exception as e:
    print(f"   ⚠ Could not check permissions: {e}")

# 6. MQTT Client
print(f"\n6. Connecting to MQTT...")
try:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.connect(MQTT_HOST, 1883, 60)
    print(f"   ✓ Connected to {MQTT_HOST}")
except Exception as e:
    print(f"   ⚠ MQTT connection failed: {e}")
    print(f"   Trying with deprecated API...")
    client = mqtt.Client()
    client.connect(MQTT_HOST, 1883, 60)

# 7. Pylontech initialisieren
print(f"\n7. Initializing Pylontech on {SERIAL_PORT}...")
try:
    battery = Pylontech(SERIAL_PORT, baudrate=BAUDRATE)
    print(f"   ✓ Successfully connected to Pylontech battery!")
except Exception as e:
    print(f"   ❌ Failed to connect: {e}")
    print(f"\n   Troubleshooting tips:")
    print(f"   - Check if cable is properly connected")
    print(f"   - Verify battery is powered on")
    print(f"   - Try different baudrate (9600, 19200, 115200)")
    print(f"   - Check if another program is using the port")
    sys.exit(1)

print("\n" + "="*60)
print("STARTING MAIN LOOP - Publishing to MQTT")
print("="*60 + "\n")

# 8. Hauptloop
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
        print(f"[{time.strftime('%H:%M:%S')}] SOC: {data.soc}% | Voltage: {data.voltage}V | Current: {data.current}A | Power: {data.voltage * data.current:.1f}W")
        
    except Exception as e:
        print(f"❌ Error in main loop: {e}")
    
    time.sleep(5)
