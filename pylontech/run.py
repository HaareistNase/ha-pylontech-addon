import time
import json
import paho.mqtt.client as mqtt
from pylontech import Pylontech
import os

# FIX: Home Assistant übergibt Konfiguration als CONFIG_* Umgebungsvariablen
SERIAL_PORT = os.getenv("CONFIG_SERIAL_PORT", "/dev/ttyUSB1")
BAUDRATE = int(os.getenv("CONFIG_BAUDRATE", "115200"))
MQTT_HOST = os.getenv("CONFIG_MQTT_HOST", "core-mosquitto")
MQTT_TOPIC = os.getenv("CONFIG_MQTT_TOPIC", "pylontech/battery")

# Optional: Debug-Ausgabe um zu sehen, welche Konfiguration verwendet wird
print(f"Using configuration: PORT={SERIAL_PORT}, BAUDRATE={BAUDRATE}, HOST={MQTT_HOST}")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)  # Veraltete API vermeiden
client.connect(MQTT_HOST, 1883, 60)

battery = Pylontech(SERIAL_PORT, baudrate=BAUDRATE)

DEBUG = os.getenv("CONFIG_DEBUG", "false").lower() == "true"
if DEBUG:
    print(f"CONFIG_SERIAL_PORT={SERIAL_PORT}")
    print(f"All CONFIG_* env vars:", {k:v for k,v in os.environ.items() if k.startswith('CONFIG_')})

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
        print(payload)

    except Exception as e:
        print("Error:", e)

    time.sleep(5)
