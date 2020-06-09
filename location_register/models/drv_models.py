from django.db import models

from data_ocean.models import DataOceanModel


class DrvRegion(DataOceanModel):
    code = models.CharField(max_length=3, unique=True)
    number = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=30, unique=True)
    short_name = models.CharField(max_length=5, unique=True)
    capital = models.CharField(max_length=20, unique=True, null=True)

    def __str__(self):
        return self.name


class DrvDistrict(DataOceanModel):
    region = models.ForeignKey(DrvRegion, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class DrvCouncil(DataOceanModel):
    region = models.ForeignKey(DrvRegion, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class DrvAto(DataOceanModel):
    """
    ATO means "адміністративно-територіальна одиниця". Central Election Comission call that name a city, 
    a district in city, a town and a village
    """
    region = models.ForeignKey(DrvRegion, on_delete=models.CASCADE)
    district = models.ForeignKey(DrvDistrict, on_delete=models.CASCADE)
    council = models.ForeignKey(DrvCouncil, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=7, unique=True)

    def __str__(self):
        return self.name


class DrvStreet(DataOceanModel):
    region = models.ForeignKey(DrvRegion, on_delete=models.CASCADE)
    district = models.ForeignKey(DrvDistrict, on_delete=models.CASCADE)
    council = models.ForeignKey(DrvCouncil, on_delete=models.CASCADE)
    ato = models.ForeignKey(DrvAto, on_delete=models.CASCADE)
    code = models.CharField(max_length=15, unique=True)
    name = models.CharField(max_length=100)
    previous_name = models.CharField(max_length=100, null=True)
    number_of_buildings = models.PositiveIntegerField(null=True)
    
    def __str__(self):
        return self.name


class ZipCode(DataOceanModel):
    region = models.ForeignKey(DrvRegion, on_delete=models.CASCADE)
    district = models.ForeignKey(DrvDistrict, on_delete=models.CASCADE)
    council = models.ForeignKey(DrvCouncil, on_delete=models.CASCADE)
    ato = models.ForeignKey(DrvAto, on_delete=models.CASCADE)
    code = models.CharField(max_length=6, unique=True)

    def __str__(self):
        return self.code


class DrvBuilding(DataOceanModel):
    INVALID = 'INVALID'
    region = models.ForeignKey(DrvRegion, on_delete=models.CASCADE)
    district = models.ForeignKey(DrvDistrict, on_delete=models.CASCADE)
    council = models.ForeignKey(DrvCouncil, on_delete=models.CASCADE)
    ato = models.ForeignKey(DrvAto, on_delete=models.CASCADE)
    street = models.ForeignKey(DrvStreet, on_delete=models.CASCADE)
    zip_code = models.ForeignKey(ZipCode, on_delete=models.CASCADE)
    code = models.CharField(max_length=20, unique=True)
    number = models.CharField(max_length=10)    
    def __str__(self):
        return self.number