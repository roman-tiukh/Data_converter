from django.db import models


class DataOceanModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    deleted_at = models.DateTimeField(null=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class Status(DataOceanModel):
    name = models.CharField(max_length=100, unique=True)


class Authority(DataOceanModel):
    name = models.CharField(max_length=500, unique=True)
    code = models.CharField(max_length=10, unique=True, null=True)


class TaxpayerType(DataOceanModel):
    name = models.CharField(max_length=200, unique=True)


class Source(DataOceanModel):
    name = models.CharField(max_length=300)


class SourceAdress(DataOceanModel):
    url_adress = models.URLField(max_length=500)
    api_adress = models.URLField(max_length=500, null=True)
    source = models.ForeignKey(Source, on_delete=models.CASCADE)


class Register(DataOceanModel):
    name = models.CharField(max_length=500)
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    url_adress = models.ForeignKey(SourceAdress, on_delete=models.CASCADE)
    api_adress = models.ForeignKey(SourceAdress, on_delete=models.CASCADE)

    def __str__(self):
        return self.name