ARG BUILD_FROM
FROM $BUILD_FROM

# Install Python
RUN apk add --no-cache python3 py3-pip

# Install Python packages
RUN pip3 install --break-system-packages pyserial paho-mqtt

# Copy script
COPY run.py /

CMD ["python3", "/run.py"]
