FROM python:3.9-alpine

ENV PYTHONUNBUFFERED 1

COPY ./app /app
COPY ./pyproject.toml  /app
COPY ./poetry.lock /app

ARG DEV=false
WORKDIR /app
EXPOSE 8000

RUN apk add --update --no-cache postgresql-client jpeg-dev && \
    apk add --update --no-cache --virtual .tmp-build-deps \
      build-base postgresql-dev musl-dev zlib zlib-dev linux-headers && \
    apk del .tmp-build-deps

RUN pip install pip --upgrade pip && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --only main

RUN if [ $DEV = "true" ];  \
      then \
        poetry install --with dev ; \
    fi
RUN adduser --disabled-password\
            --no-create-home \
            django-user

USER django-user