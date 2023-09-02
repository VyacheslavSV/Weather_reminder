import json
import logging

from django.contrib.auth.models import User
from django.utils import timezone
from django_celery_beat.models import IntervalSchedule, PeriodicTask
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from weather_app.models import Weather, City, SubscribedCity
from weather_app.serializers import WeatherSerializer, CitySerializer, SubscribedCitySerializer, UserSerializer
from weather_app.utils import get_city_data, get_weather_data_coord


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)


logger = logging.getLogger(__name__)


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = (IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        city_name = request.query_params.get('city_name')
        if not city_name:
            return super().list(request, *args, **kwargs)
        city_data = get_city_data(city_name)
        if city_data:
            return Response(city_data, status=status.HTTP_200_OK)
        return Response({'error': 'City data not found'}, status=status.HTTP_404_NOT_FOUND)


class WeatherViewSet(viewsets.ModelViewSet):
    queryset = Weather.objects.all()
    serializer_class = WeatherSerializer
    permission_classes = (IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        lat = request.query_params.get('lat')
        lon = request.query_params.get('lon')
        if lat and lon:
            return super().list(request, *args, **kwargs)
        weather_data = get_weather_data_coord(lat, lon)
        if weather_data:
            return Response(weather_data, status=status.HTTP_200_OK)
        return Response({'error': 'Weather data not found'}, status=status.HTTP_404_NOT_FOUND)


class SubscribedCityViewSet(viewsets.ModelViewSet):
    queryset = SubscribedCity.objects.all()
    serializer_class = SubscribedCitySerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        city = serializer.save(user=self.request.user)
        hours = city.period_notifications
        minutes = city.period_notifications
        interval, created = IntervalSchedule.objects.get_or_create(every=minutes, period=IntervalSchedule.MINUTES)
        subscription_info = {"email": self.request.user.email, "city": city.city.name, }
        subscription_info_json = json.dumps(subscription_info)
        startdatatime = timezone.now()
        PeriodicTask.objects.create(interval=interval, name=f'Subscriptions {self.request.user}',
                                    task='weather_app.tasks.send_weather_forecast_task',
                                    args=[self.request.user.email, city.city.name], start_time=startdatatime)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        task_name = f'Subscriptions {instance.id}'
        try:
            task = PeriodicTask.objects.get(name=task_name)
            hours = instance.period_notifications
            interval, created = IntervalSchedule.objects.get_or_create(every=hours, period=IntervalSchedule.HOURS)
            subscription_info = {'email': self.request.user.user_settings.email, 'city': instance.city.name,
                                 'country': instance.city.country}
            subscription_info_json = json.dumps(subscription_info)
            task.interval = interval
            task.kwargs = subscription_info_json
            task.save()
        except PeriodicTask.DoesNotExist as e:
            logger.error(f'PeriodicTask with name {task_name} does not exist: {str(e)}')
        logger.info(f'Updated subscription with ID {instance.id} by user {request.user.username}')
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        task_name = f'Subscriptions {instance.id}'
        try:
            task = PeriodicTask.objects.get(name=task_name)
            task.delete()
        except PeriodicTask.DoesNotExist:
            pass
        instance.delete()
        return Response({"delete": "ok"}, status=status.HTTP_204_NO_CONTENT)
