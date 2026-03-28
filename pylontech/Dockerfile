FROM python:3.11-slim

RUN pip install python-pylontech paho-mqtt pyserial

COPY run.py /run.py

CMD ["python", "/run.py"]
