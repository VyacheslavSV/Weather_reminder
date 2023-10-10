from django.core.management import BaseCommand

from weather_app.tasks import send_mail_task, get_city_weather_task
from weather_app.utils import get_city_data


# class Command(BaseCommand):
#
#     def handle(self, *args, **options):
#         print(get_city_data('london'))


class Command(BaseCommand):

    def handle(self, *args, **options):
        """
        Generate a function comment for the given function body.

        Args:
            *args: Variable length argument list.
            **options: Arbitrary keyword arguments.

        Returns:
            None.
        """
        coord = get_city_data('london')
        weather = get_city_weather_task(coord)
        print({'content': send_mail_task(weather, 'svvphotostudio@ukr.net', 'london')})
