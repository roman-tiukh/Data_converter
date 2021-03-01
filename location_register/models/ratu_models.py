from django.db import models
from django.utils.translation import ugettext_lazy as _

from data_ocean.models import DataOceanModel
from location_register.models.koatuu_models import KoatuuCategory


class RatuRegion(DataOceanModel):
    name = models.CharField(_('name'), max_length=30, help_text='Name of the region', unique=True)
    koatuu = models.CharField('code KOATUU', max_length=10, help_text='Code of the region, according to the state'
                                                                      ' classifier of objects of administrative-territorial'
                                                                      ' organization of Ukraine',
                                                                      unique=True, null=True)

    class Meta:
        verbose_name = _('region')

class RatuDistrict(DataOceanModel):
    region = models.ForeignKey(RatuRegion, on_delete=models.CASCADE, verbose_name='region')
    name = models.CharField(_('name'), help_text='Name of the district', max_length=100)
    koatuu = models.CharField('code KOATUU', max_length=10, unique=True, null=True, help_text='Code of the region, according to the state'
                                                                      ' classifier of objects of administrative-territorial'
                                                                      ' organization of Ukraine')
    code = models.CharField('code', max_length=200)

    class Meta:
        verbose_name = _('district')


class RatuCity(DataOceanModel):
    region = models.ForeignKey(RatuRegion, on_delete=models.CASCADE, verbose_name='region')
    district = models.ForeignKey(RatuDistrict, on_delete=models.CASCADE, verbose_name='district',
                                 null=True)
    category = models.ForeignKey(KoatuuCategory, on_delete=models.CASCADE, null=True,
                                 verbose_name='category')
    name = models.CharField(_('name'), max_length=100, help_text='City name')
    koatuu = models.CharField('code KOATUU', max_length=10, unique=True, null=True, help_text='Code of the region, according to the state'
                                                                      ' classifier of objects of administrative-territorial'
                                                                      ' organization of Ukraine')
    code = models.CharField('code', max_length=200)

    class Meta:
        verbose_name = _('city')


class RatuCityDistrict(DataOceanModel):
    region = models.ForeignKey(RatuRegion, on_delete=models.CASCADE, verbose_name='region')
    district = models.ForeignKey(RatuDistrict, on_delete=models.CASCADE, verbose_name='district',
                                 null=True)
    city = models.ForeignKey(RatuCity, on_delete=models.CASCADE,
                             verbose_name='city')
    category = models.ForeignKey(KoatuuCategory, on_delete=models.CASCADE, null=True,
                                 verbose_name='category')
    name = models.CharField(_('name'), help_text='Name of the city district', max_length=100)
    koatuu = models.CharField('code KOATUU', max_length=10, unique=True, null=True, help_text='Code of the region, according to the state'
                                                                      ' classifier of objects of administrative-territorial'
                                                                      ' organization of Ukraine')
    code = models.CharField('code', max_length=200)

    class Meta:
        verbose_name = _('district of the city')


class RatuStreet(DataOceanModel):
    region = models.ForeignKey(RatuRegion, on_delete=models.CASCADE, verbose_name=_('region'))
    district = models.ForeignKey(RatuDistrict, on_delete=models.CASCADE, verbose_name=_('district'),
                                 null=True)
    city = models.ForeignKey(RatuCity, on_delete=models.CASCADE,
                             verbose_name=_('city'))
    citydistrict = models.ForeignKey(RatuCityDistrict, on_delete=models.CASCADE, null=True,
                                     verbose_name=_('district of the city'))
    name = models.CharField(_('name'),help_text='City name', max_length=100)
    code = models.CharField(_('code'), max_length=200)

    class Meta:
        verbose_name = _('street')
        verbose_name_plural = _('streets')
