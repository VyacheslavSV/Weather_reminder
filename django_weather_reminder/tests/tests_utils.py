from unittest.mock import Mock

import pytest
from rest_framework.response import Response

from weather_app.utils import get_weather_data_coord, get_city_data


@pytest.fixture
def mock_requests_get(monkeypatch):
    """
    Fixture that mocks the requests.get function for testing purposes.
    Args:
        monkeypatch: A pytest fixture that allows for monkey patching of attributes or functions.
    """

    def mock_get(url):
        response = Mock()
        if 'geo' in url:
            response.status_code = 200
            response.json.return_value = [
                {'name': 'Test City', 'country': 'Test Country', 'lat': 123.456, 'lon': 789.012}]
        elif 'weather' in url:
            response.status_code = 200
            response.json.return_value = {'name': 'Test City', 'weather': [{'description': 'Sunny'}],
                                          'main': {'temp': 25.0, 'pressure': 1013.0, 'humidity': 50.0},
                                          'clouds': {'all': 0}, 'wind': {'speed': 10.0}}
        else:
            response.status_code = 500
        return response

    monkeypatch.setattr("requests.get", mock_get)


def test_get_city_data(mock_requests_get):
    """
    Test the function get_city_data by passing a mock requests.get and asserting the output.
    Parameters:
    - mock_requests_get: The mock object for the requests.get function.
    """
    city_data = get_city_data('Test City')
    assert isinstance(city_data, dict)
    assert city_data['name'] == 'Test City'
    assert city_data['country'] == 'Test Country'
    assert city_data['lat'] == 123.456
    assert city_data['lon'] == 789.012


# Test get_weather_data_coord function
def test_get_weather_data_coord(mock_requests_get):
    """
    Test the function get_weather_data_coord by mocking
    the requests.get method and asserting the returned weather data.
    Parameters:
        mock_requests_get: A mock object for the requests.get method.
    """
    weather_data = get_weather_data_coord(123.456, 789.012)
    assert isinstance(weather_data, dict)
    assert weather_data['city'] == 'Test City'
    assert weather_data['description'] == 'Sunny'
    assert weather_data['temp'] == 25.0
    assert weather_data['pressure'] == 1013.0
    assert weather_data['humidity'] == 50.0
    assert weather_data['clouds'] == 0
    assert weather_data['wind_speed'] == 10.0


# Test error handling in get_city_data function
def test_get_city_data_error(mock_requests_get):
    """
    Test the behavior of the get_city_data function when an error occurs.
    Args:
        mock_requests_get (Mock): A mocked version of the requests.get function.
    """
    city_data = get_city_data('Nonexistent City')
    assert isinstance(city_data, Response)
    assert city_data.status_code == 500
    assert 'error' in city_data.data
