from django.db import models

from data_ocean.models import DataOceanModel


class Region(DataOceanModel):
    name = models.CharField(max_length=30, unique=True)
    koatuu = models.CharField(max_length=10, unique=True, null=True)

    def __str__(self):
        return self.name


class District(DataOceanModel):
    EMPTY_FIELD = 'empty field'
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    koatuu = models.CharField(max_length=10, unique=True, null=True)

    def __str__(self):
        return self.name


class Category(DataOceanModel):
    name = (models.CharField(max_length=5, unique=True, null=True))

    def __str__(self):
        return self.name


class City(DataOceanModel):
    EMPTY_FIELD = 'empty field'
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=100)
    koatuu = models.CharField(max_length=10, unique=True, null=True)

    def __str__(self):
        return self.name


class Citydistrict(DataOceanModel):
    EMPTY_FIELD = 'empty field'
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=100)
    koatuu = models.CharField(max_length=10, unique=True, null=True)

    def __str__(self):
        return self.name


class Street(DataOceanModel):
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    citydistrict = models.ForeignKey(Citydistrict, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name