ARG BUILD_FROM
FROM $BUILD_FROM

# Installiere Python und pip
RUN apk add --no-cache python3 py3-pip

# Installiere Python-Pakete mit --break-system-packages
RUN pip3 install --no-cache-dir --break-system-packages pyserial paho-mqtt

COPY run.py /
CMD ["python3", "/run.py"]
