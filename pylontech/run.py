print("Version 2.7")

import time
import json
import paho.mqtt.client as mqtt
from pylontech import Pylontech
import os
import serial

SERIAL_PORT = os.getenv("SERIAL_PORT", "/dev/ttyUSB0")
BAUDRATE = int(os.getenv("BAUDRATE", "9600"))
MQTT_HOST = os.getenv("MQTT_HOST", "core-mosquitto")
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "pylontech/battery")

client = mqtt.Client(protocol=mqtt.MQTTv311)
client.connect(MQTT_HOST, 1883, 60)




# ✅ FIX
battery = Pylontech(SERIAL_PORT, baudrate=BAUDRATE)

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

ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=2)

while True:
    data = ser.readline()
    print("RAW:", data)
