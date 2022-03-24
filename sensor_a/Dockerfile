FROM python:3.9-alpine
RUN apk update && apk add build-base
RUN mkdir /usr/src/sensor
WORKDIR /usr/src/sensor
COPY ./requirements.txt .
RUN pip install -r requirements.txt
ENV PYTHONUNBUFFERED 1
COPY ./sensor_a.py .
ENTRYPOINT [ "python", "./sensor_a.py"]