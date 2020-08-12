from django.db import models

from data_ocean.models import DataOceanModel


class KoatuuCategory(DataOceanModel):
    name = models.CharField(max_length=20, unique=True, null=True)
    code = models.CharField(max_length=1, unique=True, null=True)


class KoatuuFirstLevel(DataOceanModel):
    name = models.CharField('назва', max_length=30, unique=True)
    code = models.CharField('код', max_length=10, unique=True, null=True)

    class Meta:
        verbose_name = 'перший рівень підпорядкованості (область або місто зі ' \
                       'спеціальним статусом)'


class KoatuuSecondLevel(DataOceanModel):
    first_level = models.ForeignKey(KoatuuFirstLevel, on_delete=models.CASCADE,
                                    verbose_name='перший рівень підпорядкованості')
    category = models.ForeignKey(KoatuuCategory, on_delete=models.CASCADE, null=True,
                                 verbose_name='категорія населеного пункта')
    name = models.CharField('назва', max_length=100)
    code = models.CharField('код', max_length=10, unique=True, null=True)

    class Meta:
        verbose_name = 'другий рівень підпорядкованості (місто, район області або ' \
                       'район міста зі спеціальним статусом)'


class KoatuuThirdLevel(DataOceanModel):
    first_level = models.ForeignKey(KoatuuFirstLevel, on_delete=models.CASCADE,
                                    verbose_name='перший рівень підпорядкованості')
    second_level = models.ForeignKey(KoatuuSecondLevel, on_delete=models.CASCADE, null=True,
                                     verbose_name='другий рівень підпорядкованості')
    category = models.ForeignKey(KoatuuCategory, on_delete=models.CASCADE, null=True,
                                 verbose_name='категорія населеного пункта')
    name = models.CharField('назва', max_length=100)
    code = models.CharField('код', max_length=10, unique=True, null=True)

    class Meta:
        verbose_name = 'третій рівень підпорядкованості (район міста обласного значення,' \
                       ' міста районного значення, селища міського типу, села)'


class KoatuuFourthLevel(DataOceanModel):
    first_level = models.ForeignKey(KoatuuFirstLevel, on_delete=models.CASCADE,
                                    verbose_name='перший рівень підпорядкованості')
    second_level = models.ForeignKey(KoatuuSecondLevel, on_delete=models.CASCADE, null=True,
                                     verbose_name='другий рівень підпорядкованості')
    third_level = models.ForeignKey(KoatuuThirdLevel, on_delete=models.CASCADE,
                                    verbose_name='третій рівень підпорядкованості')
    category = models.ForeignKey(KoatuuCategory, on_delete=models.CASCADE, null=True,
                                 verbose_name='категорія населеного пункта')
    name = models.CharField('назва', max_length=100)
    code = models.CharField('код', max_length=10, unique=True, null=True)

    class Meta:
        verbose_name = 'четвертий рівень підпорядкованості (села та селища)'
