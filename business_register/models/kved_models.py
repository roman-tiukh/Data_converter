from django.db import models
from django.utils.translation import gettext_lazy as _
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
    section = models.ForeignKey(KvedSection, on_delete=models.CASCADE, verbose_name=_('section'),
                                help_text='Section title in the classification of economic activities.')
    division = models.ForeignKey(KvedDivision, on_delete=models.CASCADE, verbose_name=_('division'),
                                 help_text='Division title in the classification of economic activities.')
    group = models.ForeignKey(KvedGroup, on_delete=models.CASCADE, verbose_name=_('group'),
                              help_text='Group title in the classification of economic activities.')
    code = models.CharField(_('code'), max_length=10, db_index=True,
                            help_text='Code in the classification of economic activities.')
    name = models.CharField(_('name'), max_length=500, help_text='Name of the type of economic activity.')
    is_valid = models.BooleanField(_('is valid'), default=True)

    class Meta:
        verbose_name = _('NACE')
        verbose_name_plural = _('Classification of economic activities')

    def __str__(self):
        return f"NACE {self.code}, name: {self.name}"
