from django.db import models
from django.contrib.auth.models import AbstractUser

from .utilites import get_timestamp_path


class AdvUser(AbstractUser):
    """Модель пользоветеля"""
    is_activated = models.BooleanField(
        default=True, db_index=True, verbose_name='Прошел активацию?'
    )
    send_message = models.BooleanField(
        default=True, verbose_name='Отправлять сообщения о новых коментариях?'
    )

    def delete(self, *args, **kwargs):
        """Переопределенный метод delete(), который удаляет пользователя и
        все связанные с ним объявления."""
        for bb in self.bb_set.all():
            bb.delete()
        super().delete(*args, **kwargs)

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


class Bb(models.Model):
    """Модель объявления с переопределенным методом delete()."""
    rubric = models.ForeignKey(SubRubric, on_delete=models.PROTECT,
                                verbose_name='Рубрика')
    title = models.CharField(max_length=40, verbose_name='Товар')
    content = models.TextField(verbose_name='Описание')
    price = models.FloatField(default=0, verbose_name='Цена')
    contacts = models.TextField(verbose_name='Контакты')
    image = models.ImageField(blank=True, upload_to=get_timestamp_path,
                              verbose_name='Изображение')
    author = models.ForeignKey(AdvUser, on_delete=models.CASCADE,
                                verbose_name='Автор объявления')
    is_active = models.BooleanField(default=True, db_index=True,
                                    verbose_name='Выводить в списке?')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True,
                                      verbose_name='Опубликовано')
    
    def delete(self, *args, **kwargs):
        """При удалении объявление удаляются так же дополнительные
        изоображения, связанные с этим же объявлением, из модели Additionalimage.
        Так же приложение django_cleanup удалит файлы, хранящиеся в удаленной записи."""
        for ai in self.additionalimage_set.all():
            ai.delete()
        super().delete(*args, **kwargs)
    
    class Meta:
        verbose_name = 'Объявление'
        verbose_name_plural = 'Объявления'
        ordering = ['-created_at']


class Additionalimage(models.Model):
    """Модель дополнительных иллюстрациий для объявления"""
    bb = models.ForeignKey(Bb, on_delete=models.CASCADE,
                           verbose_name='Объявление')
    image = models.ImageField(upload_to=get_timestamp_path,
                              verbose_name='Изображение')
    
    class Meta:
        verbose_name = 'Дополнительная иллюстрация'
        verbose_name_plural = 'Дополнительные иллюстрации'
