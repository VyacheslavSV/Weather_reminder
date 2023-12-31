import json
import logging

from django.contrib.auth.models import User
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django_celery_beat.models import IntervalSchedule, PeriodicTask
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from weather_app.models import Weather, City, SubscribedCity
from weather_app.serializers import WeatherSerializer, CitySerializer, SubscribedCitySerializer, UserSerializer
from weather_app.utils import get_city_data, get_weather_data_coord

logger = logging.getLogger(__name__)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = (IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        """
        Retrieve a list of city data based on the provided city name.

        Parameters:
            request (Request): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: The HTTP response object containing city data if found,
            or an error message if not found.
        """
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
        """
        Retrieve a list of city data based on the provided city name.

        Parameters:
            request (Request): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: The HTTP response object containing city data if found,
            or an error message if not found.
        """
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
        """
        Returns a filtered queryset based on the user making the request.

        :param self: The instance of the class.
        :return: A filtered queryset based on the user making the request.
        """
        return self.queryset.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        Create a new object.

        Args:
            request: The HTTP request object.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            A Response object with the serialized data and a status code of 201 (Created).
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        city = serializer.save(user=self.request.user)
        hours = city.period_notifications
        minutes = city.period_notifications
        interval, created = IntervalSchedule.objects.get_or_create(every=minutes, period=IntervalSchedule.MINUTES)
        subscription_info = {"email": self.request.user.email, "city": city.city.name, }
        subscription_info_json = json.dumps(subscription_info)
        startdatatime = timezone.now()
        task_name = 'weather_app.tasks.send_weather_forecast_task'
        PeriodicTask.objects.create(interval=interval, name=f'Subscriptions {self.request.user}', task=task_name,
                                    kwargs=subscription_info_json, start_time=startdatatime)
        data = serializer.data
        return Response(data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """
        Update the object specified by the request.

        Args:
            request (Request): The request object containing the data to update the object.
            args: Additional positional arguments.
            kwargs: Additional keyword arguments.

        Returns:
            Response: The response object containing the serialized data of the updated object.
        """
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
        """
        Deletes the specified instance and the associated periodic task.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: The response object with the status code indicating the success of the deletion.
        """
        instance = self.get_object()
        task_name = f'Subscriptions {instance.id}'
        try:
            task = PeriodicTask.objects.get(name=task_name)
            task.delete()
        except PeriodicTask.DoesNotExist:
            pass
        instance.delete()
        return Response({"delete": "ok"}, status=status.HTTP_204_NO_CONTENT)

#
# class SubscribedWebhookCityViewSet(viewsets.ModelViewSet):
#     queryset = SubscribedCity.objects.all()
#     serializer_class = SubscribedCitySerializer
#     permission_classes = (IsAuthenticated,)
#
#     def get_queryset(self):
#         """
#         Returns a filtered queryset based on the user making the request.
#
#         :param self: The instance of the class.
#         :return: A filtered queryset based on the user making the request.
#         """
#         return self.queryset.filter(user=self.request.user)
#
#     def create(self, request, *args, **kwargs):
#         """
#         Create a new object.
#
#         Args:
#             request: The HTTP request object.
#             *args: Additional positional arguments.
#             **kwargs: Additional keyword arguments.
#
#         Returns:
#             A Response object with the serialized data and a status code of 201 (Created).
#         """
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         city = serializer.save(user=self.request.user)
#         hours = city.period_notifications
#         minutes = city.period_notifications
#         # webhook_url = request.build_absolute_uri(reverse('weather_webhook'))
#         webhook_url = 'http://localhost:1337/webhooks/'
#         interval, created = IntervalSchedule.objects.get_or_create(every=minutes, period=IntervalSchedule.MINUTES)
#         subscription_info = {"webhook_url": webhook_url, "city": city.city.name, }
#         subscription_info_json = json.dumps(subscription_info)
#         startdatatime = timezone.now()
#         task_name = 'weather_app.tasks.send_webhook_notification_task'
#         PeriodicTask.objects.create(interval=interval, name=f'Subscriptions {self.request.user}', task=task_name,
#                                     kwargs=subscription_info_json, start_time=startdatatime)
#         data = serializer.data
#         return Response(data, status=status.HTTP_201_CREATED)
#
#     def update(self, request, *args, **kwargs):
#         """
#         Update the object specified by the request.
#
#         Args:
#             request (Request): The request object containing the data to update the object.
#             args: Additional positional arguments.
#             kwargs: Additional keyword arguments.
#
#         Returns:
#             Response: The response object containing the serialized data of the updated object.
#         """
#         instance = self.get_object()
#         serializer = self.get_serializer(instance, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         task_name = f'Subscriptions {instance.id}'
#         try:
#             task = PeriodicTask.objects.get(name=task_name)
#             hours = instance.period_notifications
#             interval, created = IntervalSchedule.objects.get_or_create(every=hours, period=IntervalSchedule.HOURS)
#             subscription_info = {'email': self.request.user.user_settings.email, 'city': instance.city.name,
#                                  'country': instance.city.country}
#             subscription_info_json = json.dumps(subscription_info)
#             task.interval = interval
#             task.kwargs = subscription_info_json
#             task.save()
#         except PeriodicTask.DoesNotExist as e:
#             logger.error(f'PeriodicTask with name {task_name} does not exist: {str(e)}')
#         logger.info(f'Updated subscription with ID {instance.id} by user {request.user.username}')
#         return Response(serializer.data)
#
#     def destroy(self, request, *args, **kwargs):
#         """
#         Deletes the specified instance and the associated periodic task.
#
#         Args:
#             request (HttpRequest): The HTTP request object.
#             *args: Variable length argument list.
#             **kwargs: Arbitrary keyword arguments.
#
#         Returns:
#             Response: The response object with the status code indicating the success of the deletion.
#         """
#         instance = self.get_object()
#         task_name = f'Subscriptions {instance.id}'
#         try:
#             task = PeriodicTask.objects.get(name=task_name)
#             task.delete()
#         except PeriodicTask.DoesNotExist:
#             pass
#         instance.delete()
#         return Response({"delete": "ok"}, status=status.HTTP_204_NO_CONTENT)
#
#
# @csrf_exempt
# def webhook(request):
#     try:
#         data = json.loads(request.body)
#
#         response_data = {'status': 'success', 'message': 'data corect'}
#         return JsonResponse(response_data)
#     except Exception as e:
#         error_response = {'status': 'error', 'message': str(e)}
#         return JsonResponse(error_response, status=400)
