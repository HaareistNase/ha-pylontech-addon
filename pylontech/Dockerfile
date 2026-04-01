ARG BUILD_FROM
FROM $BUILD_FROM

# Python und pip installieren
RUN apk add --no-cache python3 py3-pip

# Installiere Python-Pakete mit --break-system-packages (erlaubt in Docker)
RUN pip3 install --break-system-packages pyserial paho-mqtt

# Kopiere das Skript
COPY run.py /

# Startkommando
CMD ["python3", "/run.py"]
