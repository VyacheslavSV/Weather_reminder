from typing import Any

import requests
from rest_framework import status
from rest_framework.response import Response

from django_weather_reminder.settings import WEATHER_API_KEY, GEO_URL, WEATHER_URL
from weather_app.models import City
from weather_app.serializers import CitySerializer, WeatherSerializer


def get_city_data(city_name: str, lang: str = 'en') -> Response | Any:
    """
    :param city_name: The name of the city to get data for.
    :param lang: The language code for the response (default is 'en').
    :return: The city data as a dictionary.

    This method fetches data for a given city from the weather API.
    It sends a request to the GEO_URL with the city name and language code as parameters,
    along with the weather API key.
    If the response status code is 200, it extracts the city data from the response and saves
    it using the CitySerializer. The city data is then returned as a dictionary.

    If there is a problem with fetching the city data,
    a response with an error message is returned with a status code of 500.
    """
    url = GEO_URL + f'?q={city_name}&lang={lang}&appid={WEATHER_API_KEY}'
    response = requests.get(url)
    if response.status_code == 200:
        city_data = response.json()
        if city_data and city_data[0]:
            serializer_city = CitySerializer(
                data={'name': city_data[0]['name'], 'country': city_data[0]['country'], 'lat': city_data[0]['lat'],
                      'lon': city_data[0]['lon'], })
            if serializer_city.is_valid():
                existing_city = City.objects.filter(lat=city_data[0]['lat'], lon=city_data[0]['lon']).first()
                if not existing_city:
                    serializer_city.save()
            return serializer_city.data
    return Response({'error': 'Problem with fetching city data'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def get_weather_data_coord(lat: float, lon: float, units: str = 'metric', lang: str = 'en') -> Response | Any:
    """
    Get weather data for a given latitude and longitude.

    :param lat: The latitude of the location.
    :param lon: The longitude of the location.
    :param units: The unit of measurement for the weather data (default is 'metric').
    :param lang: The language code for the weather data (default is 'en').
    :return: A dictionary containing the weather data for the location.
    """
    url = WEATHER_URL + f'?lat={lat}&lon={lon}&units={units}&lang={lang}&appid={WEATHER_API_KEY}'
    response = requests.get(url)
    if response.status_code == 200:
        weather_data = response.json()
        if weather_data:
            city_name = weather_data['name']
            city = City.objects.get(name=city_name)
            serializer_weather_data = WeatherSerializer(
                data={'city': city.pk, 'description': weather_data['weather'][0]['description'],
                      'temp': weather_data['main']['temp'], 'pressure': weather_data['main']['pressure'],
                      'humidity': weather_data['main']['humidity'], 'clouds': weather_data['clouds']['all'],
                      'wind_speed': weather_data['wind']['speed'], })
            if serializer_weather_data.is_valid():
                serializer_weather_data.save()
            return serializer_weather_data.data
    return Response({'error': 'Problem with fetching weather data'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
