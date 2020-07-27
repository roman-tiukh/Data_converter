from django.db import models
from django.utils.timezone import now


class DataOceanModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    deleted_at = models.DateTimeField(null=True)

    class Meta:
        abstract = True
        ordering = ['id']

    def soft_delete(self):
        self.deleted_at = now()

    def __str__(self):
        return self.name


class Status(DataOceanModel):
    name = models.CharField('назва', max_length=100, unique=True)

    class Meta:
        verbose_name = 'статус'


class Authority(DataOceanModel):
    name = models.CharField('назва', max_length=500, unique=True)
    code = models.CharField('код ЄДРПОУ', max_length=10, unique=True, null=True)

    class Meta:
        verbose_name = 'орган реєстрації'


class TaxpayerType(DataOceanModel):
    name = models.CharField('назва', max_length=200, unique=True)

    class Meta:
        verbose_name = 'тип платника податків'


class Register(DataOceanModel):
    name = models.CharField('назва', max_length=500, unique=True)
    source_name = models.CharField('назва джерела даних', max_length=300)
    source_register_id = models.CharField('ID реєстру у джерелі даних', max_length=36, unique=True)
    data_ocean_list = models.URLField('отримати списком', max_length=500)
    data_ocean_retrieve = models.URLField("отримати об'єкт", max_length=500)
    url_address = models.URLField(max_length=500)
    api_address = models.URLField(max_length=500, null=True)
    source_last_update = models.DateTimeField('востаннє оновлено', default=None, null=True)

    class Meta:
        verbose_name = 'реєстр'

    def __str__(self):
        return self.name
