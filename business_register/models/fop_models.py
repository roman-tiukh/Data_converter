from django.db import models
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords

from business_register.models.kved_models import Kved
from data_ocean.models import DataOceanModel, Status, Authority, TaxpayerType


class Fop(DataOceanModel):
    fullname = models.CharField(_("full name"), max_length=175)
    address = models.CharField(_('address'), max_length=500, null=True)
    status = models.ForeignKey(Status, on_delete=models.CASCADE, verbose_name=_('status'))
    registration_date = models.DateField(_('registration date'), null=True, blank=True)
    registration_info = models.CharField(_('registration info'), max_length=300, null=True, blank=True)
    estate_manager = models.CharField(max_length=125, null=True, blank=True)
    termination_date = models.DateField(_('termination date'), null=True, blank=True)
    terminated_info = models.CharField(_('termination info'), max_length=300, null=True, blank=True)
    termination_cancel_info = models.CharField(_('termination cancellation info'),
                                               max_length=275, null=True, blank=True)
    contact_info = models.CharField(_('contacts'), max_length=200, null=True, blank=True)
    vp_dates = models.CharField(max_length=340, null=True, blank=True)
    authority = models.ForeignKey(Authority, on_delete=models.CASCADE,
                                  verbose_name=_('registration authority'), null=True, blank=True)
    code = models.CharField(_('our code'), max_length=675, db_index=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.fullname

    class Meta:
        ordering = ['id']
        verbose_name = _('entrepreneur')
        verbose_name_plural = _('entrepreneurs')


class FopToKved(DataOceanModel):
    fop = models.ForeignKey(Fop, related_name='kveds', on_delete=models.CASCADE, db_index=True,
                            verbose_name='entrepreneur')
    kved = models.ForeignKey(Kved, on_delete=models.CASCADE, verbose_name='NACE')
    primary_kved = models.BooleanField('declared as primary', default=False)

    def __str__(self):
        return f'{self.kved} (declared as primary)' if self.primary_kved else str(self.kved)

    class Meta:
        verbose_name = 'NACE'


class ExchangeDataFop(DataOceanModel):
    fop = models.ForeignKey(Fop, related_name='exchange_data', on_delete=models.CASCADE,
                            db_index=True, verbose_name='entrepreneur')
    authority = models.ForeignKey(Authority, null=True, on_delete=models.CASCADE,
                                  verbose_name='registration authority')
    taxpayer_type = models.ForeignKey(TaxpayerType, null=True, on_delete=models.CASCADE,
                                      verbose_name='taxpayer type')
    start_date = models.DateField(null=True)
    start_number = models.CharField(max_length=30, null=True)
    end_date = models.DateField(null=True)
    end_number = models.CharField(max_length=30, null=True)

    class Meta:
        verbose_name = _('registration info')
