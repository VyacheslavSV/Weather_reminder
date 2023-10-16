"""
URL configuration for django_weather_reminder project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.schemas import get_schema_view as get_schema_rest_fr
from rest_framework_simplejwt import views as jwt_views

from weather_app.views import webhook
from .yasg import urlpatterns as yasg_urlpatterns

urlpatterns = [path('admin/', admin.site.urls),
               # path('webhooks/', webhook, name='weather_webhook'), # webhook in procces of development
               path('api/v1/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
               path('api/v1/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
               path('api/v1/weather_reminder/', include('weather_app.urls')),
               path('api_schema/', get_schema_rest_fr(), name='api_schema'),

               ]
urlpatterns += yasg_urlpatterns
