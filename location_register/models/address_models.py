from django.db import models
from django.utils.translation import ugettext_lazy as _

from data_ocean.models import DataOceanModel


class Country(DataOceanModel):
    name = models.CharField(_('name'), max_length=60, unique=True)

    class Meta:
        verbose_name = _('country')
        verbose_name_plural = _('countries')
        ordering = ('name',)
