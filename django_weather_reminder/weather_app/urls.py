from django.urls import path, include
from rest_framework import routers

from weather_app.views import WeatherViewSet, CityViewSet, SubscribedCityViewSet, UserViewSet

router = routers.SimpleRouter()

router.register(r'users', UserViewSet)
router.register(r'cities', CityViewSet)
router.register(r'subscribes', SubscribedCityViewSet)
router.register(r'weathers', WeatherViewSet)

print(router.urls)

urlpatterns = [path('', include(router.urls)), ]
