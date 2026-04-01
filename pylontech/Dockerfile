ARG BUILD_FROM
FROM $BUILD_FROM

# Python Pakete installieren (die Base-Images haben oft schon Python)
RUN pip3 install --no-cache-dir --break-system-packages pyserial paho-mqtt

# Kopiere das Skript
COPY run.py /
CMD ["python3", "/run.py"]
