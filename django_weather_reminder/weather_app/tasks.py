import logging

from celery import shared_task, chain
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

from weather_app.utils import get_weather_data_coord, get_city_data

logger = logging.getLogger(__name__)


@shared_task
def add(x, y):
    return x + y


@shared_task(ignore_result=True)
def get_city_coordinates_task(city: str) -> dict:
    return get_city_data(city)


@shared_task(ignore_result=True)
def get_city_weather_task(coordinates: dict) -> dict:
    if not isinstance(coordinates, dict):
        raise TypeError('Parameter of function must be a dict')
    try:
        lat, lon = coordinates['lat'], coordinates['lon']
    except KeyError:
        raise KeyError('Your dict should have "lat" and "lan" keys')
    return get_weather_data_coord(lat, lon)


@shared_task
def send_mail_task(weather_data: dict, email: str, city: str) -> None:
    logger.info(f'Send mail task{email} for city {city}')
    mail_subject = 'Your weather forecast'
    context = {'city': city, 'description': weather_data.get('description'), 'temp': weather_data.get('temp'),
               'pressure': weather_data.get('pressure'), 'humidity': weather_data.get('humidity'),
               'clouds': weather_data.get('clouds'), 'wind': weather_data.get('wind_speed'), }
    message = render_to_string('weather_app/message.html', context=context)
    try:
        from_email = getattr(settings, 'EMAIL_HOST_USER')
    except AttributeError:
        raise AttributeError('You must add EMAIL_HOST_USER attribute to your settings')
    send_mail(subject=mail_subject, message=message, from_email=from_email, recipient_list=[email],
              fail_silently=False, )


@shared_task
def send_weather_forecast_task(email: str, city: str) -> None:
    try:
        logger.info(f'Sending weather forecast for city {city} to {email}')
        weather_info = chain(
            get_city_coordinates_task.s(city) | get_city_weather_task.s() | send_mail_task.s(email, city))
        weather_info.apply_async()
    except Exception as e:
        logger.error(f'Error whan sent email: {str(e)}')
