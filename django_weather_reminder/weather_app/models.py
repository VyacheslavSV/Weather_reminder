from django.contrib.auth.models import User
from django.db import models


class City(models.Model):
    class Meta:
        verbose_name = 'city'
        indexes = [models.Index(fields=['name']), ]

    name = models.CharField(max_length=255)
    country = models.CharField(max_length=255, blank=True)
    lat = models.FloatField(blank=True, null=True)
    lon = models.FloatField(blank=True, null=True)


class SubscribedCity(models.Model):
    class Meta:
        verbose_name = 'subscribed_city'
        unique_together = ('user', 'city')

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_subs')
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='city_subs')
    period_notifications = models.IntegerField()
    last_run_at = models.DateTimeField(auto_now_add=True)


class Weather(models.Model):
    class Meta:
        verbose_name = 'weather'

    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='weather_data')
    datetime = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=256)
    temp = models.FloatField()
    pressure = models.FloatField()
    humidity = models.FloatField()
    clouds = models.CharField(max_length=256)
    wind_speed = models.FloatField()
