from django.contrib.auth.models import User
from django.test import TestCase

from weather_app.models import City, SubscribedCity, Weather


class CityModelTestCase(TestCase):
    def setUp(self):
        """
        Set up the test environment by creating a test city object.
        This function does not have any parameters.
        This function does not return any values.
        """
        self.city = City.objects.create(name='Test City', country='Test Country', lat=123.456, lon=789.012)

    def test_city_model(self):
        """
        Test the city model.
        This function tests the functionality of the city model by asserting that
        the name, country, latitude, and longitude of the city object are equal to the expected values.
        Parameters:
        - self: The instance of the test class.
        """
        self.assertEqual(self.city.name, 'Test City')
        self.assertEqual(self.city.country, 'Test Country')
        self.assertEqual(self.city.lat, 123.456)
        self.assertEqual(self.city.lon, 789.012)


class SubscribedCityModelTestCase(TestCase):
    def setUp(self):
        """
        Set up the necessary objects for testing.
        This function creates a user, a city, and a subscribed city object for testing purposes.
        The user object is created with the username 'testuser'.
        The city object is created with the name 'Test City'.
        The subscribed city object is created with the user object, city object, and period_notifications value of 1.
        """
        self.user = User.objects.create(username='testuser')
        self.city = City.objects.create(name='Test City')
        self.subscribed_city = SubscribedCity.objects.create(user=self.user, city=self.city, period_notifications=1)

    def test_subscribed_city_model(self):
        """
        Test the subscribed city model.
        Asserts that the user's username is 'testuser'.
        Asserts that the city's name is 'Test City'.
        Asserts that the period notifications is 1.
        """
        self.assertEqual(self.subscribed_city.user.username, 'testuser')
        self.assertEqual(self.subscribed_city.city.name, 'Test City')
        self.assertEqual(self.subscribed_city.period_notifications, 1)


class WeatherModelTestCase(TestCase):
    def setUp(self):
        """
        Set up the test environment by creating a city object and a weather object.
        """
        self.city = City.objects.create(name='Test City')
        self.weather = Weather.objects.create(city=self.city, description='Sunny', temp=25.0, pressure=1013.0,
                                              humidity=50.0, clouds='Clear', wind_speed=10.0)

    def test_weather_model(self):
        """
        Test the weather model by asserting the values of its attributes.
        This function tests the weather model by asserting the values of
        its attributes against expected values.
        It checks if the city name is 'Test City', the description is 'Sunny',
        the temperature is 25.0, the pressure is 1013.0,
        the humidity is 50.0, the clouds are 'Clear', and the wind speed is 10.0.
        Parameters:
        - self: The instance of the test case.
        """
        self.assertEqual(self.weather.city.name, 'Test City')
        self.assertEqual(self.weather.description, 'Sunny')
        self.assertEqual(self.weather.temp, 25.0)
        self.assertEqual(self.weather.pressure, 1013.0)
        self.assertEqual(self.weather.humidity, 50.0)
        self.assertEqual(self.weather.clouds, 'Clear')
        self.assertEqual(self.weather.wind_speed, 10.0)
