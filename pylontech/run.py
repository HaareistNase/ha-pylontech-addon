import os
import sys
import json
import time
import glob
import paho.mqtt.client as mqtt
from pylontech import Pylontech

# ========== DEBUG: Alle relevanten Informationen ==========
print("\n" + "="*60)
print("PYLONTECH READER - STARTUP DEBUG")
print("="*60)

# Umgebungsvariablen
print("\n--- Relevant Environment Variables ---")
for key, value in os.environ.items():
    if any(x in key.upper() for x in ['SERIAL', 'PORT', 'CONFIG', 'TTY']):
        print(f"{key}={value}")

# Verfügbare serielle Ports
tty_devices = glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*')
print(f"\n--- Available Serial Ports ---")
print(tty_devices)

# ========== Konfiguration einlesen ==========
try:
    with open('/data/options.json') as f:
        config = json.load(f)
        SERIAL_PORT = config.get('serial_port', '/dev/ttyUSB1')
        BAUDRATE = config.get('baudrate', 115200)
        MQTT_HOST = config.get('mqtt_host', 'core-mosquitto')
        MQTT_TOPIC = config.get('mqtt_topic', 'pylontech/battery')
    print(f"\n✓ Configuration loaded from /data/options.json")
    print(f"  Config content: {json.dumps(config, indent=2)}")
except FileNotFoundError:
    print(f"\n⚠ /data/options.json not found, using environment variables")
    SERIAL_PORT = os.getenv("CONFIG_SERIAL_PORT", os.getenv("SERIAL_PORT", "/dev/ttyUSB1"))
    BAUDRATE = int(os.getenv("CONFIG_BAUDRATE", os.getenv("BAUDRATE", "115200")))
    MQTT_HOST = os.getenv("CONFIG_MQTT_HOST", os.getenv("MQTT_HOST", "core-mosquitto"))
    MQTT_TOPIC = os.getenv("CONFIG_MQTT_TOPIC", os.getenv("MQTT_TOPIC", "pylontech/battery"))

# ========== Finale Konfiguration anzeigen ==========
print(f"\n--- Final Configuration ---")
print(f"SERIAL_PORT: {SERIAL_PORT}")
print(f"BAUDRATE: {BAUDRATE}")
print(f"MQTT_HOST: {MQTT_HOST}")
print(f"MQTT_TOPIC: {MQTT_TOPIC}")
print("="*60 + "\n")

# Prüfen ob der Port existiert
if not os.path.exists(SERIAL_PORT):
    print(f"❌ ERROR: Serial port {SERIAL_PORT} does not exist!")
    print(f"Available ports: {tty_devices}")
    sys.exit(1)

# MQTT Client initialisieren
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect(MQTT_HOST, 1883, 60)

# Pylontech initialisieren
try:
    print(f"Attempting to connect to {SERIAL_PORT} at {BAUDRATE} baud...")
    battery = Pylontech(SERIAL_PORT, baudrate=BAUDRATE)
    print(f"✅ Successfully connected to {SERIAL_PORT}")
except Exception as e:
    print(f"❌ Failed to connect to {SERIAL_PORT}: {e}")
    sys.exit(1)

# Hauptloop
print("Starting main loop...")
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
        print(f"Error in main loop: {e}")

    time.sleep(5)
