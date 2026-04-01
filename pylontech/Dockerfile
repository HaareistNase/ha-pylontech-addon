ARG BUILD_FROM
FROM $BUILD_FROM

RUN apk add --no-cache python3 py3-pip
RUN pip3 install pyserial paho-mqtt

COPY run.py /
CMD ["python3", "/run.py"]
