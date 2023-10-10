from django.core.mail import send_mail
from django.core.management import BaseCommand

from django_weather_reminder.settings import EMAIL_HOST_USER


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        """
        Sends an email with a given subject, message, and recipient list.

        Parameters:
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            None
        """
        subject = 'Hi'
        message = 'I work'
        from_email = EMAIL_HOST_USER
        recipient_list = ['svvphotostudio@ukr.net']

        send_mail(subject, message, from_email, recipient_list)
