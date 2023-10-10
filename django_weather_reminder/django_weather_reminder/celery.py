import os
from datetime import timedelta

from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_weather_reminder.settings')

app = Celery('django_weather_reminder')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

CELERY_BEAT_SCHEDULE = {
    'send_weather_emails': {'task': 'weather_app.tasks.send_weather_forecast_task', 'schedule': timedelta(minutes=1),
                            'args': []}, }

app.autodiscover_tasks()

if settings.DEBUG:
    app.conf.update(task_always_eager=True)


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
