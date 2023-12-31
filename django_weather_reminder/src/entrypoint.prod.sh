#!/bin/sh

if [ "$1" = "web" ];
then
    if [ "$DATABASE" = "postgres" ];
    then
        echo "Waiting for postgres..."

        while ! nc -z $SQL_HOST $SQL_PORT; do
            sleep 0.1
        done

        echo "PostgreSQL started"
    fi

    python manage.py flush --no-input
    python manage.py migrate

    exec gunicorn django_weather_reminder.wsgi:application --bind 0.0.0.0:8000
fi

if [ "$1" = "celerybeat" ]
then
    echo "Starting Celery Beat..."
    celery -A django_weather_reminder beat -l info
else
    exec "$@"
fi

exec "$@"


