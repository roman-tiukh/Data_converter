from django.db import models

from data_ocean.models import DataOceanModel


class KvedSection(DataOceanModel):
    code = models.CharField('код', max_length=10, unique=True)
    name = models.CharField('назва', max_length=500)

    class Meta:
        verbose_name = 'секція'

    def __str__(self):
        return self.name


class KvedDivision(DataOceanModel):
    section = models.ForeignKey(KvedSection, on_delete=models.CASCADE, verbose_name='секція')
    code = models.CharField('код', max_length=10, unique=True)
    name = models.CharField('назва', max_length=500)

    class Meta:
        verbose_name = 'розділ'

    def __str__(self):
        return self.name


class KvedGroup(DataOceanModel):
    section = models.ForeignKey(KvedSection, on_delete=models.CASCADE, verbose_name='секція')
    division = models.ForeignKey(KvedDivision, on_delete=models.CASCADE, verbose_name='розділ')
    code = models.CharField('код', max_length=10, unique=True)
    name = models.CharField('назва', max_length=500)

    class Meta:
        verbose_name = 'група'

    def __str__(self):
        return self.name


class Kved(DataOceanModel):
    section = models.ForeignKey(KvedSection, on_delete=models.CASCADE, verbose_name='секція')
    division = models.ForeignKey(KvedDivision, on_delete=models.CASCADE, verbose_name='розділ')
    group = models.ForeignKey(KvedGroup, on_delete=models.CASCADE, verbose_name='група')
    code = models.CharField('код', max_length=10, db_index=True)
    name = models.CharField('назва', max_length=500)
    is_valid = models.BooleanField('є чинним', default=True)

    class Meta:
        verbose_name = 'КВЕД'

    def __str__(self):
        return f"КВЕД {self.code}, назва: {self.name}"
