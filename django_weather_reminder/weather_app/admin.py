from django.contrib import admin

from .models import City, SubscribedCity, Weather

admin.site.register(City)
admin.site.register(SubscribedCity)
admin.site.register(Weather)
