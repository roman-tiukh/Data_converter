from django.db import models

from data_ocean.models import DataOceanModel


class KvedSection(DataOceanModel):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=500)

    def __str__(self):
        return self.name


class KvedDivision(DataOceanModel):
    section = models.ForeignKey(KvedSection, on_delete=models.CASCADE)
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=500)

    def __str__(self):
        return self.name


class KvedGroup(DataOceanModel):
    section = models.ForeignKey(KvedSection, on_delete=models.CASCADE)
    division = models.ForeignKey(KvedDivision, on_delete=models.CASCADE)
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=500)

    def __str__(self):
        return self.name


class Kved(DataOceanModel):
    section = models.ForeignKey(KvedSection, on_delete=models.CASCADE)
    division = models.ForeignKey(KvedDivision, on_delete=models.CASCADE)
    group = models.ForeignKey(KvedGroup, on_delete=models.CASCADE)
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=500)
    is_valid = models.BooleanField(default=True)

    def __str__(self):
        return f"КВЕД {self.code}, назва: {self.name}"
