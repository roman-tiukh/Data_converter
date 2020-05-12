from django.db import models

from data_ocean.models.common_models import Authority, Status, TaxpayerType
from data_ocean.models.kved_models import Kved
from data_ocean.models.main import DataOceanModel
from data_ocean.models.ruo_models import State


class Rfop(DataOceanModel): 
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    kved = models.ForeignKey(Kved, on_delete=models.CASCADE)
    fullname = models.CharField(max_length=100, null=True)
    address = models.CharField(max_length=300, null=True)

    def __str__(self):
                return self.fullname


class Fop(DataOceanModel):
    #default value when there is no fullname
    INVALID = "Invalid"
    fullname = models.CharField(max_length=100)
    address = models.CharField(max_length=500, null=True)
    status = models.ForeignKey(Status, on_delete=models.CASCADE)
    registration_date = models.DateField(null=True)
    registration_info = models.CharField(max_length=300, null=True)
    estate_manager = models.CharField(max_length=100, null=True)
    termination_date = models.DateField(null=True)
    terminated_info = models.CharField(max_length=300, null=True)
    termination_cancel_info = models.CharField(max_length=100, null=True)
    contact_info = models.CharField(max_length=100, null=True)
    vp_dates = models.CharField(max_length=100, null=True)
    authority = models.ForeignKey(Authority, on_delete=models.CASCADE)

class FopToKved(DataOceanModel):
    fop = models.ForeignKey(Fop, related_name='kveds', on_delete=models.CASCADE)
    kved = models.ForeignKey(Kved, on_delete=models.CASCADE)
    primary_kved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.kved} (зазначений як основний)" if self.primary_kved else f"{self.kved}"

class ExchangeData(DataOceanModel): 
    fop = models.ForeignKey(Fop, related_name='exchange_data', on_delete=models.CASCADE)
    authority = models.ForeignKey(Authority, on_delete=models.CASCADE)
    taxpayer_type = models.ForeignKey(TaxpayerType, on_delete=models.CASCADE)
    start_date = models.DateField(null=True)
    start_number = models.CharField(max_length=20, null=True)
    end_date = models.DateField(null=True)
    end_number = models.CharField(max_length=20, null=True)