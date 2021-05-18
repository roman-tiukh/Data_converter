from django.db import models
from django.utils.translation import gettext_lazy as _

from data_ocean.models import DataOceanModel


class Country(DataOceanModel):
    name = models.CharField(_('english name'), max_length=60, unique=True)
    name_uk = models.CharField(_('ukrainian name'), max_length=100, null=True, default=None, unique=True)
    nacp_id = models.PositiveIntegerField(_('NACP id of country'), null=True, default=None, unique=True)

    class Meta:
        verbose_name = _('country')
        verbose_name_plural = _('countries')
        ordering = ('name',)
