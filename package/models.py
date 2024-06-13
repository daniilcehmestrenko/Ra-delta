import uuid

from django.db import models
from django.contrib.sessions.models import Session


class Package(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True,
    )
    session = models.ForeignKey(
        Session,
        verbose_name='Id сессии пользователя',
        on_delete=models.SET_NULL,
        db_index=True,
        blank=True,
        null=True,
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=100,
    )
    weight = models.DecimalField(
        verbose_name='Вес в кг',
        max_digits=10,
        decimal_places=3,
    )
    type_package = models.ForeignKey(
        'TypePackage',
        related_name='packages',
        verbose_name='Тип посылки',
        on_delete=models.CASCADE,
    )
    cost_in_usd = models.DecimalField(
        verbose_name='Стоимость в $',
        max_digits=20,
        decimal_places=2,
    )
    delivery_cost = models.DecimalField(
        verbose_name='Стоимость доставки в ₽',
        max_digits=20,
        decimal_places=2,
        blank=True,
        null=True,
        default=None,
    )
    delivery_company = models.ForeignKey(
        'DeliveryCompany',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        default=None,
    )

    @property
    def type_package_name(self):
        return str(self.type_package)


class TypePackage(models.Model):
    CLOTH = 'CL'
    ELECTRONIC = 'EL'
    VARIA = 'VR'
    CHOICES = (
        (CLOTH, 'Одежда'),
        (ELECTRONIC, 'Электроника'),
        (VARIA, 'Разное'),
    )
    name = models.CharField(
        verbose_name='Тип посылки',
        max_length=2,
        choices=CHOICES,
    )

    def get_name_display(self, type_p):
        types = {
            self.CLOTH: 'Одежда',
            self.ELECTRONIC: 'Электроника',
            self.VARIA: 'Разное'
        }
        return types.get(type_p)

    def __str__(self):
        return self.get_name_display(self.name)


class DeliveryCompany(models.Model):
    name = models.CharField(
        verbose_name='Название компании',
        max_length=100,
    )

    def __str__(self):
        return self.name
