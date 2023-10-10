import json

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from weather_app.models import City, SubscribedCity


@pytest.mark.django_db
def test_city_list_view():
    """
    Test the city_list_view function.
    This function tests the city_list_view function in the Django application.
    It checks the behavior of the view when called with and without the city_name parameter.
    Raises:
    - AssertionError: If any of the test conditions fail.
    """
    client = APIClient()
    url = reverse('city-list')

    # Test without city_name parameter
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK

    # Test with city_name parameter
    response = client.get(url, {'city_name': 'Test City'})
    assert response.status_code == status.HTTP_200_OK
    data = json.loads(response.content)
    assert data['name'] == 'Test City'


@pytest.mark.django_db
def test_weather_list_view():
    """
    Test the weather list view.
    This function tests the weather list view by making HTTP GET requests
    to the specified URL with and without lat and lon parameters.
    It asserts that the response status code is 200 OK and checks
    the returned data for the expected city name and weather description.
    """
    client = APIClient()
    url = reverse('weather-list')

    # Test without lat and lon parameters
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK

    # Test with lat and lon parameters
    response = client.get(url, {'lat': 123.456, 'lon': 789.012})
    assert response.status_code == status.HTTP_200_OK
    data = json.loads(response.content)
    assert data['city'] == 'Test City'
    assert data['description'] == 'Sunny'


@pytest.mark.django_db
def test_subscribed_city_create_view():
    """
    Test the create, update, and delete functionality of the subscribed city view.
    This function uses the Django test framework and the APIClient to simulate HTTP requests
     to the subscribed city API endpoints. It performs the following tests:
    - Test the creation of a subscribed city by sending a POST request with the necessary data.
    - Test the update of a subscribed city by sending a PUT request with updated data.
    - Test the deletion of a subscribed city by sending a DELETE request.
    """
    client = APIClient()
    url = reverse('subscribedcity-list')

    user = User.objects.create(username='testuser', password='testpassword')
    city = City.objects.create(name='Test City')

    client.force_authenticate(user=user)

    # Test create subscribed city
    data = {'user': user.id, 'city': city.id, 'period_notifications': 1}
    response = client.post(url, data, format='json')
    assert response.status_code == status.HTTP_201_CREATED

    # Test update subscribed city
    subscribed_city = SubscribedCity.objects.get(user=user)
    data = {'period_notifications': 2}
    response = client.put(reverse('subscribedcity-detail', args=[subscribed_city.id]), data, format='json')
    assert response.status_code == status.HTTP_200_OK
    subscribed_city.refresh_from_db()
    assert subscribed_city.period_notifications == 2

    # Test delete subscribed city
    response = client.delete(reverse('subscribedcity-detail', args=[subscribed_city.id]))
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not SubscribedCity.objects.filter(user=user).exists()
