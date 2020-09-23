from django.db import models

from data_ocean.models import DataOceanModel
from location_register.models.koatuu_models import KoatuuCategory


class RatuRegion(DataOceanModel):
    name = models.CharField('назва', max_length=30, unique=True)
    koatuu = models.CharField('код КОАТУУ', max_length=10, unique=True, null=True)

    class Meta:
        verbose_name = 'регіон'


class RatuDistrict(DataOceanModel):
    region = models.ForeignKey(RatuRegion, on_delete=models.CASCADE, verbose_name='регіон')
    name = models.CharField('назва', max_length=100)
    koatuu = models.CharField('код КОАТУУ', max_length=10, unique=True, null=True)
    code = models.CharField('код', max_length=200)

    class Meta:
        verbose_name = 'район'


class RatuCity(DataOceanModel):
    region = models.ForeignKey(RatuRegion, on_delete=models.CASCADE, verbose_name='регіон')
    district = models.ForeignKey(RatuDistrict, on_delete=models.CASCADE, verbose_name='район',
                                 null=True)
    category = models.ForeignKey(KoatuuCategory, on_delete=models.CASCADE, null=True,
                                 verbose_name='категорія населеного пункта')
    name = models.CharField('назва', max_length=100)
    koatuu = models.CharField('код КОАТУУ', max_length=10, unique=True, null=True)
    code = models.CharField('код', max_length=200)

    class Meta:
        verbose_name = 'населенний пункт'


class RatuCityDistrict(DataOceanModel):
    region = models.ForeignKey(RatuRegion, on_delete=models.CASCADE, verbose_name='регіон')
    district = models.ForeignKey(RatuDistrict, on_delete=models.CASCADE, verbose_name='район',
                                 null=True)
    city = models.ForeignKey(RatuCity, on_delete=models.CASCADE,
                             verbose_name='населений пункт')
    category = models.ForeignKey(KoatuuCategory, on_delete=models.CASCADE, null=True,
                                 verbose_name='категорія населеного пункта')
    name = models.CharField('назва', max_length=100)
    koatuu = models.CharField('код КОАТУУ', max_length=10, unique=True, null=True)
    code = models.CharField('', max_length=200)

    class Meta:
        verbose_name = 'район у місті'


class RatuStreet(DataOceanModel):
    region = models.ForeignKey(RatuRegion, on_delete=models.CASCADE, verbose_name='регіон')
    district = models.ForeignKey(RatuDistrict, on_delete=models.CASCADE, verbose_name='район',
                                 null=True)
    city = models.ForeignKey(RatuCity, on_delete=models.CASCADE,
                             verbose_name='населений пункт')
    citydistrict = models.ForeignKey(RatuCityDistrict, on_delete=models.CASCADE, null=True,
                                     verbose_name='район у місті')
    name = models.CharField('назва', max_length=100)
    code = models.CharField('код', max_length=200)

    class Meta:
        verbose_name = 'вулиця'
