from django.db import models
from django.utils.translation import ugettext_lazy as _
from data_ocean.models import DataOceanModel


class KvedSection(DataOceanModel):
    code = models.CharField('code', max_length=10, unique=True)
    name = models.CharField('name', max_length=500)

    class Meta:
        verbose_name = _('section')

    def __str__(self):
        return self.name


class KvedDivision(DataOceanModel):
    section = models.ForeignKey(KvedSection, on_delete=models.CASCADE, verbose_name='section')
    code = models.CharField('code', max_length=10, unique=True)
    name = models.CharField('name', max_length=500)

    class Meta:
        verbose_name = _('division')

    def __str__(self):
        return self.name


class KvedGroup(DataOceanModel):
    section = models.ForeignKey(KvedSection, on_delete=models.CASCADE, verbose_name='section')
    division = models.ForeignKey(KvedDivision, on_delete=models.CASCADE, verbose_name='division')
    code = models.CharField('code', max_length=10, unique=True)
    name = models.CharField('name', max_length=500)

    class Meta:
        verbose_name = _('group')

    def __str__(self):
        return self.name


class Kved(DataOceanModel):
    section = models.ForeignKey(KvedSection, on_delete=models.CASCADE, verbose_name=_('section'))
    division = models.ForeignKey(KvedDivision, on_delete=models.CASCADE, verbose_name=_('division'))
    group = models.ForeignKey(KvedGroup, on_delete=models.CASCADE, verbose_name=_('group'))
    code = models.CharField(_('code'), max_length=10, db_index=True)
    name = models.CharField(_('name'), max_length=500)
    is_valid = models.BooleanField(_('is valid'), default=True)

    class Meta:
        verbose_name = _('NACE')
        verbose_name_plural = _('Classification of economic activities')

    def __str__(self):
        return f"NACE {self.code}, name: {self.name}"
