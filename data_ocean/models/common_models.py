from django.db import models
from data_ocean.models.main import DataOceanModel

class Status(DataOceanModel):
    name = models.CharField(max_length=100, unique=True)

class Authority(DataOceanModel):
    name = models.CharField(max_length=500, unique=True)
    code = models.CharField(max_length=10, unique=True, null=True)

class TaxpayerType(DataOceanModel):
    name = models.CharField(max_length=200, unique=True)