from django.apps import AppConfig
from django.dispatch import Signal

from .utilites import send_activation_notification


class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'
    verbose_name = 'Доска Объявлений'

user_registered = Signal()

def user_registered_dispather(sender, **kwargs):
    send_activation_notification(kwargs['instance'])

user_registered.connect(user_registered_dispather)
