from django.db import models
from django.contrib.auth.models import AbstractUser


class AdvUser(AbstractUser):
    """Модель пользоветеля"""
    is_activated = models.BooleanField(
        default=True, db_index=True, verbose_name='Прошел активацию?'
    )
    send_message = models.BooleanField(
        default=True, verbose_name='Отправлять сообщения о новых коментариях?'
    )

    class Meta(AbstractUser.Meta):
        pass


class Rubric(models.Model):
    """Базовая модель рубрики"""
    name = models.CharField(
        max_length=20, db_index=True,
        unique=True, verbose_name='Название'
    )
    order = models.SmallIntegerField(
        default=0, db_index=True,
        verbose_name='Порядок'
    )
    super_rubric = models.ForeignKey(
        'SuperRubric', on_delete=models.PROTECT,
        null=True, blank=True, verbose_name='Надрубрика'
    )


class SuperRubricManager(models.Manager):
    """Класс диспетчера записей для класса надрубрик.
    Надрубрики не могут иметь надрубрики, поэтому поле
    super_rubric должно быть пустым."""
    def get_queryset(self):
        return super().get_queryset().filter(super_rubric__isnull=True)


class SuperRubric(Rubric):
    """Прокси-модель надрубрик, изменяющий функиональность модели Rubric.
    Диспетчер записей SuperRubricManager"""
    objects = SuperRubricManager()
    def __str__(self):
        return self.name
    
    class Meta:
        proxy = True
        ordering = ('order', 'name')
        verbose_name = 'Надрубрика'
        verbose_name_plural = 'Надрубрики'


class SubRubricManager(models.Manager):
    """Класс диспетчера записей для класса подрубрики.
    Подрубрики должны иметь надрубрики, поэтому поле
    super_rubric должно быть заполнено."""
    def get_queryset(self):
        return super().get_queryset().filter(super_rubric__isnull=False)


class SubRubric(Rubric):
    """Прокси-модель подрубрик, изменяющий функиональность модели Rubric.
    Диспетчер записей SubRubricManager"""
    objects = SubRubricManager()

    def __str__(self):
        return '%s - %s' % (self.super_rubric.name, self.name)
    
    class Meta:
        proxy = True
        ordering = (
            'super_rubric__order', 'super_rubric__name',
            'order', 'name'
        )
        verbose_name = 'Подрубрика'
        verbose_name_plural = 'Подрубрики'