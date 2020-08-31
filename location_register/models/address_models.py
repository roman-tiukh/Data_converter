from django.db import models

from data_ocean.models import DataOceanModel


class Country(DataOceanModel):
    name = models.CharField('назва', max_length=60, unique=True)

    class Meta:
        verbose_name = 'країна'
