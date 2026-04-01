import time
import json
import paho.mqtt.client as mqtt
from pylontech import Pylontech
import os
import sys

# Konfiguration aus Home Assistant Add-on Umgebungsvariablen
SERIAL_PORT = os.getenv("CONFIG_SERIAL_PORT", "/dev/ttyUSB1")
BAUDRATE = int(os.getenv("CONFIG_BAUDRATE", "115200"))
MQTT_HOST = os.getenv("CONFIG_MQTT_HOST", "core-mosquitto")
MQTT_TOPIC = os.getenv("CONFIG_MQTT_TOPIC", "pylontech/battery")

# Debug-Ausgabe
print(f"Starting Pylontech Reader with:")
print(f"  SERIAL_PORT: {SERIAL_PORT}")
print(f"  BAUDRATE: {BAUDRATE}")
print(f"  MQTT_HOST: {MQTT_HOST}")
print(f"  MQTT_TOPIC: {MQTT_TOPIC}")

# MQTT Client mit neuer API
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect(MQTT_HOST, 1883, 60)

# Pylontech initialisieren - direkt mit dem Port-String
try:
    battery = Pylontech(SERIAL_PORT, baudrate=BAUDRATE)
    print(f"Successfully connected to {SERIAL_PORT}")
except Exception as e:
    print(f"Failed to connect to {SERIAL_PORT}: {e}")
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
        print(f"Error in main loop: {e}")

    time.sleep(5)
