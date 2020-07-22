from django.db import models

class DataOceanModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    deleted_at = models.DateTimeField(null=True)

    class Meta:
        abstract = True
        ordering = ['id']

    def __str__(self):
        return self.name


class Status(DataOceanModel):
    name = models.CharField(max_length=100, unique=True)


class Authority(DataOceanModel):
    name = models.CharField(max_length=500, unique=True)
    code = models.CharField(max_length=10, unique=True, null=True)


class TaxpayerType(DataOceanModel):
    name = models.CharField(max_length=200, unique=True)


class Register(DataOceanModel):
    name = models.CharField(max_length=500, unique=True)
    source_name = models.CharField(max_length=300)
    source_register_id = models.CharField(max_length=36, unique=True)
    data_ocean_list = models.URLField(max_length=500)
    data_ocean_retrieve = models.URLField(max_length=500)
    url_address = models.URLField(max_length=500)
    api_address = models.URLField(max_length=500, null=True)
    source_last_update = models.DateTimeField(default=None, null=True)

    def __str__(self):
        return self.name
