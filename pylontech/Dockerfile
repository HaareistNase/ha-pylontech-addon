ARG BUILD_FROM
FROM $BUILD_FROM

# Installiere Python und pip
RUN apk add --no-cache python3 py3-pip

# Installiere Python-Pakete
RUN pip3 install --no-cache-dir pyserial paho-mqtt

COPY run.py /
CMD ["python3", "/run.py"]
