FROM python:3.11
ARG TELEGRAM_TOKEN
ENV TELEGRAM_TOKEN=$TELEGRAM_TOKEN
ENV PORT 8080

RUN apt-get update && apt-get install -y libgl1

RUN pip install --upgrade pip

COPY requirements.txt /

RUN pip install -r requirements.txt

COPY ./src /src
#COPY .env /.env

CMD uvicorn src.main:app --host 0.0.0.0 --port ${PORT}