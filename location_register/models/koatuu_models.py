from django.db import models
from django.utils.translation import ugettext_lazy as _

from data_ocean.models import DataOceanModel


class KoatuuCategory(DataOceanModel):
    name = models.CharField(max_length=20, unique=True, null=True)
    code = models.CharField(max_length=1, unique=True, null=True)

    class Meta:
        verbose_name = _('category')


class KoatuuFirstLevel(DataOceanModel):
    name = models.CharField(_('name'), max_length=30, unique=True)
    code = models.CharField(_('code'), max_length=10, unique=True, null=True)

    class Meta:
        verbose_name = _('first level (region or city with special status)')
        verbose_name_plural = _('first level (regions or cities with special status)')


class KoatuuSecondLevel(DataOceanModel):
    first_level = models.ForeignKey(KoatuuFirstLevel, on_delete=models.CASCADE,
                                    related_name='second_level_places',
                                    verbose_name=_('first level'))
    category = models.ForeignKey(KoatuuCategory, on_delete=models.CASCADE, null=True,
                                 verbose_name=_('category'))
    name = models.CharField(_('name'), max_length=100)
    code = models.CharField(_('code'), max_length=10, unique=True, null=True)

    class Meta:
        verbose_name = _('second level (city, district of the region)')
        verbose_name_plural = _('second level (cities, districts of the region)')


class KoatuuThirdLevel(DataOceanModel):
    first_level = models.ForeignKey(KoatuuFirstLevel, on_delete=models.CASCADE,
                                    verbose_name=_('first level'))
    second_level = models.ForeignKey(KoatuuSecondLevel, on_delete=models.CASCADE, null=True,
                                     related_name='third_level_places',
                                     verbose_name=_('second level'))
    category = models.ForeignKey(KoatuuCategory, on_delete=models.CASCADE, null=True,
                                 verbose_name=_('category'))
    name = models.CharField(_('name'), max_length=100)
    code = models.CharField(_('code'), max_length=10, unique=True, null=True)

    class Meta:
        verbose_name = _('third level (district of the city of regional significance,'
                         ' city of district significance,'
                         ' urban-type settlement,'
                         ' village)')
        verbose_name_plural = _('third level (districts of the cities of regional significance,'
                                ' cities of district significance,'
                                ' urban-type settlements,'
                                ' villages)')


class KoatuuFourthLevel(DataOceanModel):
    first_level = models.ForeignKey(KoatuuFirstLevel, on_delete=models.CASCADE,
                                    verbose_name=_('first level'))
    second_level = models.ForeignKey(KoatuuSecondLevel, on_delete=models.CASCADE, null=True,
                                     verbose_name=_('second level'))
    third_level = models.ForeignKey(KoatuuThirdLevel, on_delete=models.CASCADE,
                                    related_name='fourth_level_places',
                                    verbose_name=_('third level'))
    category = models.ForeignKey(KoatuuCategory, on_delete=models.CASCADE, null=True,
                                 verbose_name=_('category'))
    name = models.CharField(_('name'), max_length=100)
    code = models.CharField(_('code'), max_length=10, unique=True, null=True)

    class Meta:
        verbose_name = _('fourth level of subordination (village or settlement)')
        verbose_name_plural = _('fourth level of subordination (villages and settlements)')
