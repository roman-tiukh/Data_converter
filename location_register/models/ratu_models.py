from django.db import models

from data_ocean.models import DataOceanModel
from location_register.models.koatuu_models import KoatuuCategory


class RatuRegion(DataOceanModel):
    name = models.CharField(max_length=30, unique=True)
    koatuu = models.CharField(max_length=10, unique=True, null=True)


class RatuDistrict(DataOceanModel):
    EMPTY_FIELD = 'empty field'
    region = models.ForeignKey(RatuRegion, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    koatuu = models.CharField(max_length=10, unique=True, null=True)


class RatuCity(DataOceanModel):
    EMPTY_FIELD = 'empty field'
    region = models.ForeignKey(RatuRegion, on_delete=models.CASCADE)
    district = models.ForeignKey(RatuDistrict, on_delete=models.CASCADE)
    category = models.ForeignKey(KoatuuCategory, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=100)
    koatuu = models.CharField(max_length=10, unique=True, null=True)


class RatuCityDistrict(DataOceanModel):
    EMPTY_FIELD = 'empty field'
    region = models.ForeignKey(RatuRegion, on_delete=models.CASCADE)
    district = models.ForeignKey(RatuDistrict, on_delete=models.CASCADE)
    city = models.ForeignKey(RatuCity, on_delete=models.CASCADE)
    category = models.ForeignKey(KoatuuCategory, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=100)
    koatuu = models.CharField(max_length=10, unique=True, null=True)


class RatuStreet(DataOceanModel):
    region = models.ForeignKey(RatuRegion, on_delete=models.CASCADE)
    district = models.ForeignKey(RatuDistrict, on_delete=models.CASCADE)
    city = models.ForeignKey(RatuCity, on_delete=models.CASCADE)
    citydistrict = models.ForeignKey(RatuCityDistrict, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
