FROM python:3.11-alpine

WORKDIR /usr/src/django_weather_reminder

ENV PYTHONDONTWRITEBITECODE 1
ENV PYTHONBUFFERED 1

#RUN apk update \
#    && apk add postgresql-dev gcc python3-dev musl-dev

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libcairo2-dev \
        postgresql-dev \
        gcc \
        python3-dev \
        musl-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
COPY /requirements.txt .
RUN pip install -r requirements.txt

COPY entrypoint.sh .
RUN sed -i 's/\r$//g' /usr/src/django_weather_reminder/entrypoint.sh
RUN chmod +x /usr/src/django_weather_reminder/entrypoint.sh

COPY .. .

ENTRYPOINT ["/usr/src/django_weather_reminder/entrypoint.sh"]
