from django.db import models
from django.contrib.auth.models import AbstractUser


class AdvUser(AbstractUser):
    is_activated = models.BooleanField(
        default=True, db_index=True, verbose_name='Прошел активацию?'
    )
    send_message = models.BooleanField(
        default=True, verbose_name='Отправлять сообщения о новых коментариях?'
    )

    class Meta(AbstractUser.Meta):
        pass