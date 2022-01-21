FROM python:3.8.5-alpine

COPY . /app
WORKDIR /app

RUN apk add --no-cache mariadb-connector-c-dev
RUN apk update
RUN apk update && apk add bash tk wkhtmltopdf python3 python3-dev mariadb-dev build-base && pip3 install mysqlclient && pip3 install pip --upgrade

RUN apk add netcat-openbsd

RUN pip install -r requirements.txt
