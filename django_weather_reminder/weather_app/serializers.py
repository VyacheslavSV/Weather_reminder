from django.contrib.auth.models import User
from rest_framework import serializers

from .models import City, SubscribedCity, Weather


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'email']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['name', 'country', 'lat', 'lon']


class SubscribedCitySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscribedCity
        fields = ['user', 'city', 'period_notifications']


class WeatherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Weather
        fields = ['city', 'description', 'temp', 'pressure', 'humidity', 'clouds', 'wind_speed']
