from django.contrib.auth.models import User
from django.test import TestCase

from weather_app.models import City
from weather_app.serializers import UserSerializer, CitySerializer, SubscribedCitySerializer, WeatherSerializer


class UserSerializerTestCase(TestCase):
    def test_user_serializer(self):
        """
        Test the UserSerializer class.
        This function creates a test user with a username, password, and email.
        It then creates an instance of the UserSerializer class using the test data.
        The function asserts that the serializer is valid and saves the user.
        Finally, it asserts that the username of the saved user matches the provided username.
        Parameters:
        - self: The instance of the test case.
        """
        data = {'username': 'testuser', 'password': 'testpassword', 'email': 'test@example.com'}
        serializer = UserSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.username, 'testuser')


class CitySerializerTestCase(TestCase):
    def test_city_serializer(self):
        """
        Test the CitySerializer class by creating a test city with specified data and asserting its validity.
        """
        data = {'name': 'Test City', 'country': 'Test Country', 'lat': 123.456, 'lon': 789.012}
        serializer = CitySerializer(data=data)
        self.assertTrue(serializer.is_valid())
        city = serializer.save()
        self.assertEqual(city.name, 'Test City')


class SubscribedCitySerializerTestCase(TestCase):
    def test_subscribed_city_serializer(self):
        """
        Test the SubscribedCitySerializer.
        This function creates a test user and a test city, then creates a data dictionary with the user
        ID, city ID, and period_notifications value. It then creates an instance of the SubscribedCitySerializer
        with the data and checks if it is valid using the `is_valid()` method. If it is valid, it saves the
        serializer and checks if the `user.username` attribute of the saved subscribed_city object is equal
        to 'testuser'.
        Parameters:
        - self: The instance of the test case class.
        Raises:
        - AssertionError: If the `is_valid()` method returns False or if the `user.username` attribute of the
                          saved subscribed_city object is not equal to 'testuser'.
        """
        user = User.objects.create(username='testuser')
        city = City.objects.create(name='Test City')
        data = {'user': user.id, 'city': city.id, 'period_notifications': 1}
        serializer = SubscribedCitySerializer(data=data)
        self.assertTrue(serializer.is_valid())
        subscribed_city = serializer.save()
        self.assertEqual(subscribed_city.user.username, 'testuser')


class WeatherSerializerTestCase(TestCase):
    def test_weather_serializer(self):
        """
        Test the WeatherSerializer class.
        This function creates a test city object and a test data dictionary. It then initializes the WeatherSerializer
        with the test data and asserts that the serializer is valid. The function saves the serialized data to the
        database and asserts that the city name is correctly saved.
        Parameters:
            self (TestClass): An instance of the test class.
        """
        city = City.objects.create(name='Test City')
        data = {'city': city.id, 'description': 'Sunny', 'temp': 25.0, 'pressure': 1013.0, 'humidity': 50.0,
                'clouds': 'Clear', 'wind_speed': 10.0}
        serializer = WeatherSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        weather = serializer.save()
        self.assertEqual(weather.city.name, 'Test City')
