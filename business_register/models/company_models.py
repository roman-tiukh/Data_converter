from django.db import models
from django.utils.translation import ugettext_lazy as _
from simple_history.models import HistoricalRecords

from business_register.models.kved_models import Kved
from data_ocean.models import Authority, DataOceanModel, Status, TaxpayerType
from location_register.models.address_models import Country


class Bylaw(DataOceanModel):
    name = models.CharField(verbose_name='name', max_length=320, unique=True, null=True, help_text=_('Company name'))

    class Meta:
        verbose_name = _('charter')


class CompanyType(DataOceanModel):
    name = models.CharField('name', max_length=270, unique=True, null=True, help_text=_('Company name'))
    name_eng = models.CharField("name in Company House (UK companies` register)",
                                max_length=270, unique=True, null=True, help_text=_('Company name in Company House'))

    class Meta:
        verbose_name = _('company type')


class Company(DataOceanModel):  # constraint for not null in both name & short_name fields
    UKRAINE_REGISTER = 'ukr'
    GREAT_BRITAIN_REGISTER = 'gb'
    ANTAC = 'antac'
    SOURCES = (
        (UKRAINE_REGISTER,
         _(
             'The United State Register of Legal Entities, Individual Entrepreneurs and Public Organizations of Ukraine')),
        (GREAT_BRITAIN_REGISTER, _('Company House (UK companies` register)')),
        (ANTAC, _('ANTAC')),
    )

    INVALID = 'invalid'  # constant for empty edrpou fild etc.
    name = models.CharField(_('name'), max_length=500, null=True, help_text=_('Company name'))
    short_name = models.CharField(_('short name'), max_length=500, null=True, help_text=_('Short name'))
    company_type = models.ForeignKey(CompanyType, on_delete=models.CASCADE, null=True,
                                     verbose_name=_('company type'), help_text=_('Type of company'))
    edrpou = models.CharField(_('number'), max_length=260, null=True, db_index=True, help_text=_('EDRPOU'))
    boss = models.CharField(_('CEO'), max_length=100, null=True, blank=True, default='', help_text=_('CEO of company'))
    authorized_capital = models.FloatField(_('share capital'), null=True, help_text=_('Authorized capital'))
    country = models.ForeignKey(Country, max_length=60, on_delete=models.CASCADE, null=True,
                                verbose_name=_('country'), help_text=_('Country of origin'))
    address = models.CharField(_('address'), max_length=1000, null=True, help_text=_('Address'))
    status = models.ForeignKey(Status, on_delete=models.CASCADE, null=True,
                               verbose_name=_('status'), help_text=_('Status'))
    bylaw = models.ForeignKey(Bylaw, on_delete=models.CASCADE, null=True,
                              verbose_name=_('charter'), help_text=_('By law'))
    registration_date = models.DateField(_('registration date'), null=True, help_text=_('Registration date'))
    registration_info = models.CharField(_('registration info'), max_length=450, null=True,
                                         help_text=_('Registration info'))
    contact_info = models.CharField(_('contacts'), max_length=310, null=True, help_text=_('Info about contacts'))
    authority = models.ForeignKey(Authority, on_delete=models.CASCADE, null=True,
                                  verbose_name=_('registration authority'), help_text=_('Authority'))
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True,
                               verbose_name=_('parent company'), help_text=_('Parent company'))
    antac_id = models.PositiveIntegerField(_("id from ANTACs DB"), unique=True,
                                           db_index=True, null=True, default=None, blank=True,
                                           help_text=_('ID from ANTACs DB'))
    from_antac_only = models.BooleanField(null=True)
    source = models.CharField(_('source'), max_length=5, choices=SOURCES, null=True,
                              blank=True, default=None, db_index=True, help_text=_('Source'))
    code = models.CharField(_('our code'), max_length=510, db_index=True, help_text=_('Our code'))
    history = HistoricalRecords()

    @property
    def founder_of(self):
        if not self.edrpou:
            return []
        founder_of = Founder.objects.filter(edrpou=self.edrpou)
        founded_companies = []
        for founder in founder_of:
            founded_companies.append(founder.company)
        return founded_companies

    @property
    def founder_of_count(self):
        if not self.edrpou:
            return 0
        return Founder.objects.filter(edrpou=self.edrpou).count()

    @property
    def is_closed(self):
        if not self.status:
            return None
        return self.status.name == 'припинено'

    @property
    def is_foreign(self):
        if not self.country:
            return None
        return self.country.name != 'ukraine'

    class Meta:
        verbose_name = _('company')
        verbose_name_plural = _('companies')
        index_together = [
            ('edrpou', 'source')
        ]


class Assignee(DataOceanModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='assignees',
                                verbose_name='є правонаступником', help_text=_('Company is the legal successor'))
    name = models.CharField('name', max_length=610, null=True, help_text=_('Company name'))
    edrpou = models.CharField('number', max_length=11, null=True, help_text=_('EDRPOU'))
    history = HistoricalRecords()

    class Meta:
        verbose_name = _('assignee')


class BancruptcyReadjustment(DataOceanModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE,
                                related_name='bancruptcy_readjustment', help_text=_('Bankruptcy readjustment'))
    op_date = models.DateField(null=True, help_text=_('Date'))
    reason = models.TextField('reason', null=True, help_text=_('Reason of bankruptcy'))
    sbj_state = models.CharField(max_length=345, null=True, help_text=_('Subject state'))
    head_name = models.CharField(max_length=515, null=True, help_text=_('Head name'))
    history = HistoricalRecords()

    def __str__(self):
        return self.sbj_state

    class Meta:
        verbose_name = _('bankruptcy readjustment')


class CompanyDetail(DataOceanModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='company_detail',
                                help_text=_('Company name'))
    founding_document_number = models.CharField(max_length=375, null=True, help_text=_('Founding document number'))
    executive_power = models.CharField(max_length=390, null=True, help_text=_('Executive power'))
    superior_management = models.CharField(max_length=620, null=True, help_text=_('Superior management'))
    managing_paper = models.CharField(max_length=360, null=True, help_text=_('Managing paper'))
    terminated_info = models.CharField(max_length=600, null=True, help_text=_('Info about termination'))
    termination_cancel_info = models.CharField(max_length=570, null=True,
                                               help_text=_('Info about termination cancellation'))
    vp_dates = models.TextField(null=True, help_text=_('Dates'))
    history = HistoricalRecords()

    class Meta:
        verbose_name = _('additional info')


class CompanyToKved(DataOceanModel):  # constraint for only only one truth in primary field
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='kveds', help_text=_('Company name'))
    kved = models.ForeignKey(Kved, on_delete=models.CASCADE, verbose_name='NACE', help_text=_('NACE'))
    primary_kved = models.BooleanField('declared as primary', default=False, help_text=_('Primary NACE'))
    history = HistoricalRecords()

    class Meta:
        verbose_name = _('NACE')

    def __str__(self):
        return f"{self.kved} (declared as primary)" if self.primary_kved else self.kved


class ExchangeDataCompany(DataOceanModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='exchange_data',
                                help_text=_('Company name'))
    authority = models.ForeignKey(Authority, on_delete=models.CASCADE,
                                  verbose_name='registration authority', help_text=_('Registration authority'))
    taxpayer_type = models.ForeignKey(TaxpayerType, on_delete=models.CASCADE, null=True, help_text=_('Taxpayer type'))
    start_date = models.DateField(null=True, help_text=_('Start date'))
    start_number = models.CharField(max_length=555, null=True, help_text=_('Start number'))
    end_date = models.DateField(null=True, help_text=_('End date'))
    end_number = models.CharField(max_length=555, null=True, help_text=_('End number'))
    history = HistoricalRecords()

    def __str__(self):
        return self.authority.name

    class Meta:
        verbose_name = _('registration info')


class Founder(DataOceanModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='founders',
                                verbose_name='owner', help_text=_('Company name'))
    info = models.CharField('info', max_length=2015, help_text=_('Info'))
    info_additional = models.CharField('additional info', max_length=2015, null=True, help_text=_('Additional info'))
    info_beneficiary = models.CharField('beneficiary info', max_length=2015, null=True,
                                            help_text=_('Beneficiary Info'))
    name = models.TextField("name or full name", db_index=True, help_text=_('Name'))
    edrpou = models.CharField('number', max_length=9, null=True, blank=True, default='',
                              db_index=True, help_text=_('EDRPOU'))
    equity = models.FloatField('equity', null=True, blank=True, help_text=_('Equity'))
    address = models.CharField('address', max_length=2015, null=True, blank=True, default='', help_text=_('Address'))
    country = models.CharField('country', max_length=100, null=True, blank=True, default='',
                               help_text=_('Country of origin'))
    is_beneficiary = models.BooleanField('is beneficiary', blank=True, default=False, help_text=_('Is beneficiary'))
    is_founder = models.BooleanField('is owner', blank=True, default=False, help_text=_('Is founder'))
    history = HistoricalRecords()

    # retrieving id only for founder that is company
    @property
    def id_if_company(self):
        if self.edrpou:
            company = Company.objects.filter(edrpou=self.edrpou).first()
            if company:
                return company.id
        return None

    class Meta:
        verbose_name = _('owner')


class Predecessor(DataOceanModel):  # constraint for not null in both fields
    name = models.CharField('name', max_length=500, null=True, help_text=_('Name'))
    edrpou = models.CharField('number', max_length=405, null=True, help_text=_('EDRPOU'))

    class Meta:
        verbose_name = _('predecessor')


class CompanyToPredecessor(DataOceanModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='predecessors',
                                help_text=_('Company name'))
    predecessor = models.ForeignKey(Predecessor, on_delete=models.CASCADE, help_text=_('Predecessor'))
    history = HistoricalRecords()

    def __str__(self):
        return self.predecessor.name


class Signer(DataOceanModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='signers', help_text=_('Company name'))
    name = models.CharField("full name", max_length=390, null=True, help_text=_('Name'))
    history = HistoricalRecords()

    class Meta:
        verbose_name = _('signer')


class TerminationStarted(DataOceanModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE,
                                related_name='termination_started', help_text=_('Company name'))
    op_date = models.DateField(null=True, help_text=_('Date'))
    reason = models.TextField('reason', null=True, help_text=_('Reason of termination'))
    sbj_state = models.CharField(max_length=530, null=True, help_text=_('State'))
    signer_name = models.CharField(max_length=480, null=True, help_text=_('Signer name'))
    creditor_reg_end_date = models.DateField(null=True,  help_text=_('Creditor registration end date'))
    history = HistoricalRecords()

    def __str__(self):
        return self.sbj_state

    class Meta:
        verbose_name = _("termination")
