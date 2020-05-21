from django.db import models

from data_ocean.models import DataOceanModel


class Section(DataOceanModel):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=500)

    def __str__(self):
        return self.name


class Division(DataOceanModel):
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    code = models.CharField(max_length=5, unique=True)
    name = models.CharField(max_length=500)

    def __str__(self):
        return self.name


class Group(DataOceanModel):
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    division = models.ForeignKey(Division, on_delete=models.CASCADE)
    code = models.CharField(max_length=5, unique=True)
    name = models.CharField(max_length=500)

    def __str__(self):
        return self.name


class Kved(DataOceanModel):
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    division = models.ForeignKey(Division, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    code = models.CharField(max_length=5, unique=True)
    name = models.CharField(max_length=500)

    def __str__(self):
        return f"КВЕД {self.code}, назва: {self.name}"
