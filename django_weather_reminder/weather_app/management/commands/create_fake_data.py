import random

from django.contrib.auth.models import User
from django.core.management import BaseCommand
from django.utils import timezone
from faker import Faker

from weather_app.models import City, SubscribedCity, Weather

fake = Faker()


class Command(BaseCommand):
    """
    Function create fake data and save in database.
    """

    def handle(self, *args, **kwargs):
        """
        Handles the creation of users, cities, and weather data for testing purposes.

        Parameters:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            None
        """
        users = []
        cities = []
        for _ in range(10):
            username = fake.user_name()
            email = fake.email()
            password = fake.password()
            user = User.objects.create_user(username=username, email=email, password=password)
        for _ in range(10):
            name = fake.city()
            country = fake.country()
            state = fake.state()
            units = random.choice(['metric', 'imperial'])
            lat = fake.latitude()
            lon = fake.longitude()

            City.objects.create(name=name, country=country, state=state, units=units, lat=lat, lon=lon)
            cities.append(name)

        for user in users:
            for _ in range(1):
                city_name = random.choice(cities)
                city = City.objects.get(name=city_name)
                period_notifications = random.randint(1, 3)
                last_run_at = timezone.now()

                SubscribedCity.objects.create(user=user, city=city, period_notifications=period_notifications,
                                              last_run_at=last_run_at)

        for _ in range(5):
            city_name = random.choice(cities)
            city = City.objects.get(name=city_name)
            datetime = fake.date_time_this_year(tzinfo=timezone.get_current_timezone())
            description = fake.word()
            temp = fake.random_int(min=0, max=40)
            pressure = fake.random_int(min=900, max=1100)
            humidity = fake.random_int(min=0, max=100)
            clouds = fake.word()
            wind_speed = fake.random_int(min=0, max=30)

            Weather.objects.create(city=city, datetime=datetime, description=description, temp=temp, pressure=pressure,
                                   humidity=humidity, clouds=clouds, wind_speed=wind_speed)
