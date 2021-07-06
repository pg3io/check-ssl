FROM python:3.7-alpine

WORKDIR /usr/src/app
COPY requirements.txt ./
RUN apk add --no-cache --virtual build-dependencies build-base gcc wget git && pip install --no-cache-dir -r requirements.txt && apk del build-dependencies build-base gcc wget git

COPY  check_ssl.py /usr/src/app/main.py
RUN mkdir /sources && touch /sources/list.yml
COPY ./sources/list.yml /sources/list.yml
ENV LIST="/sources/list.yml"
VOLUME ["/sources/"]

CMD [ "python", "-u", "main.py" ]

