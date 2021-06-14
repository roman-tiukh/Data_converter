from django.db import models
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords

from business_register.models.kved_models import Kved
from data_ocean.models import Authority, DataOceanModel, Status, TaxpayerType
from data_ocean.transliteration.utils import transliterate, translate_country_in_string
from location_register.models.address_models import Country


class Bylaw(DataOceanModel):
    name = models.CharField(verbose_name='name', max_length=320, unique=True, null=True,
                            help_text='Company name in Ukrainian')

    class Meta:
        verbose_name = _('charter')


class CompanyType(DataOceanModel):
    name = models.CharField('name', max_length=270, unique=True, null=True, help_text='Company name in Ukrainian')
    name_eng = models.CharField("name in Company House (UK companies` register)",
                                max_length=270, unique=True, null=True,
                                help_text='Company name in Company House (UK companies` register)')

    class Meta:
        verbose_name = _('company type')


class Company(DataOceanModel):  # constraint for not null in both name & short_name fields
    UKRAINE_REGISTER = 'ukr'
    GREAT_BRITAIN_REGISTER = 'gb'
    ANTAC = 'antac'
    DECLARATIONS = 'decl'
    SOURCES = (
        (UKRAINE_REGISTER,
         _(
             'The United State Register of Legal Entities, Individual Entrepreneurs and Public Organizations of Ukraine')),
        (GREAT_BRITAIN_REGISTER, _('Company House (UK companies` register)')),
        (ANTAC, _('ANTAC')),
        (DECLARATIONS, _('Declarations')),
    )

    INVALID = 'invalid'  # constant for empty edrpou fild etc.
    name = models.CharField(_('name'), max_length=500, null=True, help_text='Company name in Ukrainian')
    name_en = models.CharField(_('english name'), max_length=500, null=True, help_text='Company name in English')
    short_name = models.CharField(_('short name'), max_length=500, null=True,
                                  help_text='Short name of the company in Ukrainian')
    company_type = models.ForeignKey(CompanyType, on_delete=models.CASCADE, null=True,
                                     verbose_name=_('company type'), help_text='Type of the company')
    edrpou = models.CharField(_('number'), max_length=260, null=True, db_index=True,
                              help_text='EDRPOU number as string')
    boss = models.CharField(_('CEO'), max_length=100, null=True, blank=True, default='',
                            help_text='CEO of the company')
    authorized_capital = models.FloatField(_('share capital'), null=True, help_text='Authorized capital as number')
    country = models.ForeignKey(Country, max_length=60, on_delete=models.CASCADE, null=True,
                                verbose_name=_('country'), help_text='Country of origin')
    address = models.CharField(_('address'), max_length=1000, null=True,
                               help_text='Registration address in Ukrainian')
    status = models.ForeignKey(
        Status,
        on_delete=models.CASCADE,
        null=True,
        verbose_name=_('status'),
        help_text='Company legal status. Can be: "зареєстровано", "в стані припинення", "припинено", "EMP", "порушено '
                  'справу про банкрутство", "порушено справу про банкрутство (санація)", "зареєстровано, свідоцтво про '
                  'державну реєстрацію недійсне", "скасовано", "active", "active - proposal to strike off", "liquidation",'
                  ' "administration order", "voluntary arrangement", "in administration/administrative receiver", '
                  '"in administration", "live but receiver manager on at least one charge", "in administration/receiver '
                  'manager", "receivership", "receiver manager / administrative receiver", "administrative receiver", '
                  'voluntary arrangement / administrative receiver", "voluntary arrangement / receiver manager".'
    )
    bylaw = models.ForeignKey(Bylaw, on_delete=models.CASCADE, null=True,
                              verbose_name=_('charter'), help_text='By law')
    registration_date = models.DateField(_('registration date'), null=True,
                                         help_text='Registration date as string in YYYY-MM-DD format')
    registration_info = models.CharField(_('registration info'), max_length=450, null=True,
                                         help_text='Registration info of the company')
    contact_info = models.TextField(_('contacts'), null=True, help_text='Info about contacts')
    authority = models.ForeignKey(Authority, on_delete=models.CASCADE, null=True,
                                  verbose_name=_('registration authority'),
                                  help_text='Authorized state agency which register the company')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True,
                               verbose_name=_('parent company'),
                               help_text='Company that has a controlling interest in the company')
    antac_id = models.PositiveIntegerField(_("id from ANTACs DB"), unique=True,
                                           db_index=True, null=True, default=None, blank=True,
                                           help_text='ID from ANTACs DB')
    from_antac_only = models.BooleanField(null=True, help_text='If this field has "true" - '
                                                               'Data provided by the Anti-Corruption Action Center.')
    source = models.CharField(_('source'), max_length=5, choices=SOURCES, null=True,
                              blank=True, default=None, db_index=True, help_text='Source')
    code = models.CharField(_('our code'), max_length=510, db_index=True, help_text='Our code')
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

    @property
    def address_en(self):
        if self.address:
            return transliterate(translate_country_in_string(self.address))
        else:
            return None


    class Meta:
        verbose_name = _('company')
        verbose_name_plural = _('companies')
        index_together = [
            ('edrpou', 'source')
        ]


class Assignee(DataOceanModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='assignees',
                                verbose_name='є правонаступником', help_text='Company is the legal successor')
    name = models.CharField('name', max_length=610, blank=True, default='', help_text='Assignee name in Ukrainian')
    edrpou = models.CharField('number', max_length=11, blank=True, default='', help_text='EDRPOU number as string')
    history = HistoricalRecords()

    class Meta:
        verbose_name = _('assignee')


class BancruptcyReadjustment(DataOceanModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE,
                                related_name='bancruptcy_readjustment', help_text='Bankruptcy readjustment')
    op_date = models.DateField(null=True, help_text='Date of bankruptcy readjustment as string in YYYY-MM-DD format')
    reason = models.TextField('reason', null=True, help_text='Reason of bankruptcy')
    sbj_state = models.CharField(max_length=345, null=True, help_text='Subject state')
    head_name = models.CharField(max_length=515, null=True, help_text='Head name')
    history = HistoricalRecords()

    def __str__(self):
        return self.sbj_state

    class Meta:
        verbose_name = _('bankruptcy readjustment')


class CompanyDetail(DataOceanModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='company_detail',
                                help_text='Company name')
    founding_document_number = models.CharField(max_length=375, null=True,
                                                help_text='Founding document number as string')
    executive_power = models.CharField(max_length=390, null=True, help_text='Executive power of the company')
    superior_management = models.CharField(max_length=620, null=True, help_text='Superior management of the company')
    managing_paper = models.CharField(max_length=360, null=True, help_text='Managing paper of the company')
    terminated_info = models.CharField(max_length=600, null=True, help_text='Info about termination')
    termination_cancel_info = models.CharField(max_length=570, null=True,
                                               help_text='Info about termination cancellation')
    vp_dates = models.TextField(null=True, help_text='Array of dates as string in YYYY-MM-DD format')
    history = HistoricalRecords()

    class Meta:
        verbose_name = _('additional info')


class CompanyToKved(DataOceanModel):  # constraint for only only one truth in primary field
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='kveds',
                                help_text='Company name')
    kved = models.ForeignKey(Kved, on_delete=models.CASCADE, verbose_name='NACE', help_text='NACE as string')
    primary_kved = models.BooleanField('declared as primary', default=False, help_text='Primary NACE as string')
    history = HistoricalRecords()

    class Meta:
        verbose_name = _('NACE')

    def __str__(self):
        return f"{self.kved} (declared as primary)" if self.primary_kved else str(self.kved)


class ExchangeDataCompany(DataOceanModel):
    company = company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='exchange_data',
                                          help_text='Company name')
    authority = models.ForeignKey(Authority, on_delete=models.CASCADE,
                                  verbose_name='registration authority',
                                  help_text='Authorized state agency which register the company')
    taxpayer_type = models.ForeignKey(TaxpayerType, on_delete=models.CASCADE, null=True,
                                      help_text='Taxpayer type of the company')
    start_date = models.DateField(null=True, help_text='Start date as string in YYYY-MM-DD format')
    start_number = models.CharField(max_length=555, null=True, help_text='Start number')
    end_date = models.DateField(null=True, help_text='End date as string in YYYY-MM-DD format')
    end_number = models.CharField(max_length=555, null=True, help_text='End number')
    history = HistoricalRecords()

    def __str__(self):
        return self.authority.name

    class Meta:
        verbose_name = _('registration info')


class Founder(DataOceanModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='founders',
                                verbose_name='owner', help_text='Company name')
    info = models.TextField('info', help_text='Info')
    info_additional = models.TextField('additional info', null=True, help_text='Additional info')
    info_beneficiary = models.TextField('beneficiary info', null=True, help_text='Beneficiary Info')
    name = models.TextField("name or full name", db_index=True, help_text='Founder name in Ukrainian')
    edrpou = models.CharField('number', max_length=9, null=True, blank=True, default='',
                              db_index=True, help_text='EDRPOU number as string')
    equity = models.FloatField('equity', null=True, blank=True, help_text='Equity')
    address = models.TextField('address', null=True, blank=True, default='', help_text='Founder address in Ukrainian')
    country = models.CharField('country', max_length=100, null=True, blank=True, default='',
                               help_text='Country of origin')
    is_beneficiary = models.BooleanField('is beneficiary', blank=True, default=False,
                                         help_text='Is beneficiary of the company')
    is_founder = models.BooleanField('is owner', blank=True, default=False, help_text='Is founder of the company')
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
    name = models.CharField('name', max_length=500, null=True, help_text='Predecessor name in Ukrainian')
    edrpou = models.CharField('number', max_length=405, null=True, help_text='EDRPOU number as string')

    class Meta:
        verbose_name = _('predecessor')


class CompanyToPredecessor(DataOceanModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='predecessors',
                                help_text='Company name')
    predecessor = models.ForeignKey(Predecessor, on_delete=models.CASCADE, help_text='Predecessor name in Ukrainian')
    history = HistoricalRecords()

    def __str__(self):
        return self.predecessor.name


class Signer(DataOceanModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='signers',
                                help_text='Company name')
    name = models.CharField("full name", max_length=390, null=True, help_text='Signer name in Ukrainian')
    history = HistoricalRecords()

    class Meta:
        verbose_name = _('signer')


class TerminationStarted(DataOceanModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE,
                                related_name='termination_started', help_text='Company name')
    op_date = models.DateField(null=True, help_text='Date as string in YYYY-MM-DD format')
    reason = models.TextField('reason', null=True, help_text='Reason of termination')
    sbj_state = models.CharField(max_length=530, null=True, help_text='State of the company')
    signer_name = models.CharField(max_length=480, null=True, help_text='Signer name in Ukrainian')
    creditor_reg_end_date = models.DateField(null=True,
                                             help_text='Creditor registration end date as string in YYYY-MM-DD format')
    history = HistoricalRecords()

    def __str__(self):
        return self.sbj_state

    class Meta:
        verbose_name = _("termination")
