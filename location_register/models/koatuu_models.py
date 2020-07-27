from django.db import models

from data_ocean.models import DataOceanModel


class KoatuuCategory(DataOceanModel):
    name = (models.CharField(max_length=5, unique=True, null=True))


class KoatuuRegion(DataOceanModel):
    name = models.CharField('назва', max_length=30, unique=True)
    code = models.CharField('код', max_length=10, unique=True, null=True)

    class Meta:
        verbose_name = 'регіон'


class KoatuuDistrict(DataOceanModel):
    region = models.ForeignKey(KoatuuRegion, on_delete=models.CASCADE, verbose_name='регіон')
    name = models.CharField('назва', max_length=100)
    code = models.CharField('код', max_length=10, unique=True, null=True)

    class Meta:
        verbose_name = 'район'

class KoatuuCity(DataOceanModel):
    region = models.ForeignKey(KoatuuRegion, on_delete=models.CASCADE, verbose_name='регіон')
    district = models.ForeignKey(KoatuuDistrict, on_delete=models.CASCADE, null=True,
                                 verbose_name='район')
    category = models.ForeignKey(KoatuuCategory, on_delete=models.CASCADE, null=True,
                                 verbose_name='категорія населеного пункта')
    name = models.CharField('назва', max_length=100)
    code = models.CharField('код', max_length=10, unique=True, null=True)


class KoatuuCityDistrict(DataOceanModel):
    region = models.ForeignKey(KoatuuRegion, on_delete=models.CASCADE, verbose_name='регіон')
    district = models.ForeignKey(KoatuuDistrict, on_delete=models.CASCADE, null=True,
                                 verbose_name='район')
    city = models.ForeignKey(KoatuuCity, on_delete=models.CASCADE,
                             verbose_name='населений пункт')
    category = models.ForeignKey(KoatuuCategory, on_delete=models.CASCADE, null=True,
                                 verbose_name='категорія населеного пункта')
    name = models.CharField('назва', max_length=100)
    code = models.CharField('код', max_length=10, unique=True, null=True)

    class Meta:
        verbose_name = 'район у місті'
