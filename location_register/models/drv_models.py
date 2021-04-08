from django.db import models
from django.utils.translation import gettext_lazy as _

from data_ocean.models import DataOceanModel


class DrvRegion(DataOceanModel):
    code = models.CharField('code', max_length=3, unique=True)
    number = models.CharField('number', max_length=3, unique=True)
    name = models.CharField('name', max_length=30, unique=True)
    short_name = models.CharField('short_name', max_length=5, unique=True)
    capital = models.CharField('capital', max_length=20, unique=True, null=True)

    class Meta:
        verbose_name = _('region')


class DrvDistrict(DataOceanModel):
    region = models.ForeignKey(DrvRegion, on_delete=models.CASCADE, verbose_name='region')
    name = models.CharField('name', max_length=50)
    code = models.CharField('code', max_length=80, unique=True, null=True)

    class Meta:
        verbose_name = _('district')


class DrvCouncil(DataOceanModel):
    region = models.ForeignKey(DrvRegion, on_delete=models.CASCADE, verbose_name='region')
    name = models.CharField('name', max_length=100)
    code = models.CharField('code', max_length=130, unique=True, null=True)

    class Meta:
        verbose_name = _('council')


class DrvAto(DataOceanModel):
    """
    ATO means "адміністративно-територіальна одиниця". Central Election Comission call that name a city, 
    a district in city, a town and a village
    """
    region = models.ForeignKey(DrvRegion, on_delete=models.CASCADE, verbose_name='region')
    district = models.ForeignKey(DrvDistrict, on_delete=models.CASCADE, verbose_name='district')
    council = models.ForeignKey(DrvCouncil, on_delete=models.CASCADE, verbose_name='council')
    name = models.CharField('name', max_length=100)
    code = models.CharField('code', max_length=7, unique=True)

    class Meta:
        verbose_name = _('administrative-territorial unit')


class DrvStreet(DataOceanModel):
    region = models.ForeignKey(DrvRegion, on_delete=models.CASCADE, verbose_name='region')
    district = models.ForeignKey(DrvDistrict, on_delete=models.CASCADE, verbose_name='district')
    council = models.ForeignKey(DrvCouncil, on_delete=models.CASCADE)
    ato = models.ForeignKey(DrvAto, on_delete=models.CASCADE)
    code = models.CharField('code', max_length=15, unique=True)
    name = models.CharField('name', max_length=155)
    previous_name = models.TextField('previous name', null=True)
    number_of_buildings = models.PositiveIntegerField('number of buildings', null=True)

    class Meta:
        verbose_name = _('street')


class ZipCode(DataOceanModel):
    region = models.ForeignKey(DrvRegion, on_delete=models.CASCADE, verbose_name='region')
    district = models.ForeignKey(DrvDistrict, on_delete=models.CASCADE, verbose_name='district')
    council = models.ForeignKey(DrvCouncil, on_delete=models.CASCADE, verbose_name='council')
    ato = models.ForeignKey(DrvAto, on_delete=models.CASCADE,
                            verbose_name='administrative-territorial unit')
    code = models.CharField('ZIP code', max_length=6, unique=True)

    class Meta:
        verbose_name = _('ZIP code')

    def __str__(self):
        return self.code


class DrvBuilding(DataOceanModel):
    INVALID = 'INVALID'
    region = models.ForeignKey(DrvRegion, on_delete=models.CASCADE, verbose_name=_('region'))
    district = models.ForeignKey(DrvDistrict, on_delete=models.CASCADE, verbose_name=_('district'))
    council = models.ForeignKey(DrvCouncil, on_delete=models.CASCADE, verbose_name=_('council'))
    ato = models.ForeignKey(DrvAto, on_delete=models.CASCADE,
                            verbose_name=_('administrative-territorial unit'))
    street = models.ForeignKey(DrvStreet, on_delete=models.CASCADE, verbose_name=_('street'))
    zip_code = models.ForeignKey(ZipCode, on_delete=models.CASCADE,
                                 verbose_name=_('ZIP code'))
    code = models.CharField(_('code'), max_length=20, unique=True)
    number = models.CharField(max_length=58)

    def __str__(self):
        return self.number

    class Meta:
        verbose_name = _('building')
        verbose_name_plural = _('buildings')
