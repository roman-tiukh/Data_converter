from django.db import models

from data_ocean.models import DataOceanModel
from location_register.models.koatuu_models import KoatuuCategory


class RatuRegion(DataOceanModel):
    name = models.CharField('назва', max_length=30, unique=True)
    koatuu = models.CharField('код КОАТУУ', max_length=10, unique=True, null=True)

    class Meta:
        verbose_name = 'регіон'


class RatuDistrict(DataOceanModel):
    EMPTY_FIELD = 'empty field'
    region = models.ForeignKey(RatuRegion, on_delete=models.CASCADE, verbose_name='регіон')
    name = models.CharField('назва', max_length=100)
    koatuu = models.CharField('код КОАТУУ', max_length=10, unique=True, null=True)

    class Meta:
        verbose_name = 'район'


class RatuCity(DataOceanModel):
    EMPTY_FIELD = 'empty field'
    region = models.ForeignKey(RatuRegion, on_delete=models.CASCADE, verbose_name='регіон')
    district = models.ForeignKey(RatuDistrict, on_delete=models.CASCADE, verbose_name='район')
    category = models.ForeignKey(KoatuuCategory, on_delete=models.CASCADE, null=True,
                                 verbose_name='категорія населеного пункта')
    name = models.CharField('назва', max_length=100)
    koatuu = models.CharField('код КОАТУУ', max_length=10, unique=True, null=True)


class RatuCityDistrict(DataOceanModel):
    EMPTY_FIELD = 'empty field'
    region = models.ForeignKey(RatuRegion, on_delete=models.CASCADE, verbose_name='регіон')
    district = models.ForeignKey(RatuDistrict, on_delete=models.CASCADE, verbose_name='район')
    city = models.ForeignKey(RatuCity, on_delete=models.CASCADE,
                             verbose_name='населений пункт')
    category = models.ForeignKey(KoatuuCategory, on_delete=models.CASCADE, null=True,
                                 verbose_name='категорія населеного пункта')
    name = models.CharField('назва', max_length=100)
    koatuu = models.CharField('код КОАТУУ', max_length=10, unique=True, null=True)

    class Meta:
        verbose_name = 'район у місті'


class RatuStreet(DataOceanModel):
    region = models.ForeignKey(RatuRegion, on_delete=models.CASCADE, verbose_name='регіон')
    district = models.ForeignKey(RatuDistrict, on_delete=models.CASCADE, verbose_name='район')
    city = models.ForeignKey(RatuCity, on_delete=models.CASCADE,
                             verbose_name='населений пункт')
    citydistrict = models.ForeignKey(RatuCityDistrict, on_delete=models.CASCADE,
                                     verbose_name='район у місті')
    name = models.CharField('назва', max_length=100)
