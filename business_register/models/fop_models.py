from django.db import models
from simple_history.models import HistoricalRecords

from business_register.models.kved_models import Kved
from data_ocean.models import DataOceanModel, Status, Authority, TaxpayerType


class Fop(DataOceanModel):
    # default value when there is no fullname
    INVALID = "Invalid"
    fullname = models.CharField("повне ім'я", max_length=100)
    address = models.CharField('адреса', max_length=500, null=True)
    status = models.ForeignKey(Status, on_delete=models.CASCADE, verbose_name='статус')
    registration_date = models.DateField('дата реєстрації', null=True)
    registration_info = models.CharField('реєстраційні дані', max_length=300, null=True)
    estate_manager = models.CharField(max_length=125, null=True)
    termination_date = models.DateField(null=True)
    terminated_info = models.CharField(max_length=300, null=True)
    termination_cancel_info = models.CharField(max_length=275, null=True)
    contact_info = models.CharField('контакти', max_length=200, null=True)
    vp_dates = models.CharField(max_length=140, null=True)
    authority = models.ForeignKey(Authority, on_delete=models.CASCADE,
                                  verbose_name='орган реєстрації')
    code = models.CharField(max_length=600, db_index=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'фізична особа-підприємець'

    def __str__(self):
        return self.fullname


class FopToKved(DataOceanModel):
    fop = models.ForeignKey(Fop, related_name='kveds', on_delete=models.CASCADE, db_index=True,
                            verbose_name='ФОП')
    kved = models.ForeignKey(Kved, on_delete=models.CASCADE, verbose_name='КВЕД')
    primary_kved = models.BooleanField('зазначений як основний', default=False)

    def __str__(self):
        return f"{self.kved} (зазначений як основний)" if self.primary_kved else f"{self.kved}"

    class Meta:
        verbose_name = 'КВЕДи ФОП'


class ExchangeDataFop(DataOceanModel):
    fop = models.ForeignKey(Fop, related_name='exchange_data', on_delete=models.CASCADE,
                            db_index=True, verbose_name='ФОП')
    authority = models.ForeignKey(Authority, on_delete=models.CASCADE,
                                  verbose_name='орган реєстрації')
    taxpayer_type = models.ForeignKey(TaxpayerType, null=True, on_delete=models.CASCADE,
                                      verbose_name='тип платника податків')
    start_date = models.DateField(null=True)
    start_number = models.CharField(max_length=30, null=True)
    end_date = models.DateField(null=True)
    end_number = models.CharField(max_length=30, null=True)
