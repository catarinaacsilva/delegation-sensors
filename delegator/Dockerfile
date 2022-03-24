FROM python:3.9-alpine
RUN apk update && apk add build-base
RUN mkdir /usr/src/delegator
WORKDIR /usr/src/delegator
COPY ./requirements.txt .
RUN pip install -r requirements.txt
ENV PYTHONUNBUFFERED 1
COPY ./delegator.py .
ENTRYPOINT [ "python", "./delegator.py"]
