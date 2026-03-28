import time
import json
import serial
import paho.mqtt.client as mqtt
from pylontech import Pylontech
import os

SERIAL_PORT = os.getenv("SERIAL_PORT", "/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_ABSCDIG1-if00-port0")
BAUDRATE = int(os.getenv("BAUDRATE", "115200"))
MQTT_HOST = os.getenv("MQTT_HOST", "core-mosquitto")
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "pylontech/battery")

client = mqtt.Client()
client.connect(MQTT_HOST, 1883, 60)

ser = serial.Serial(SERIAL_PORT, baudrate=BAUDRATE, timeout=2)
battery = Pylontech(ser)

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
