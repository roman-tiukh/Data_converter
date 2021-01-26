from django.db import models
from simple_history.models import HistoricalRecords

from business_register.models.kved_models import Kved
from data_ocean.models import Authority, DataOceanModel, Status, TaxpayerType
from location_register.models.address_models import Country


class Bylaw(DataOceanModel):
    name = models.CharField(verbose_name='статут', max_length=320, unique=True, null=True)

    class Meta:
        verbose_name = 'статут'


class CompanyType(DataOceanModel):
    name = models.CharField('назва', max_length=270, unique=True, null=True)
    name_eng = models.CharField('назва англійською', max_length=270, unique=True, null=True)

    class Meta:
        verbose_name = 'організаційно-правова форма'


class Company(DataOceanModel):  # constraint for not null in both name & short_name fields
    UKRAINE_REGISTER = 'ukr'
    GREAT_BRITAIN_REGISTER = 'gb'
    ANTAC = 'antac'
    SOURCES = (
        (UKRAINE_REGISTER,
         'Єдиний державний реєстр юридичних осіб, фізичних осіб – підприємців та громадських формувань України'),
        (GREAT_BRITAIN_REGISTER, 'Companies House'),
        (ANTAC, 'Центр протидії корупції'),
    )

    INVALID = 'invalid'  # constant for empty edrpou fild etc.
    name = models.CharField('назва', max_length=500, null=True)
    short_name = models.CharField('коротка назва', max_length=500, null=True)
    company_type = models.ForeignKey(CompanyType, on_delete=models.CASCADE, null=True,
                                     verbose_name='організаційно-правова форма')
    edrpou = models.CharField('код ЄДРПОУ', max_length=260, null=True, db_index=True)
    boss = models.CharField('керівник', max_length=100, null=True, blank=True, default='')
    authorized_capital = models.FloatField('статутний капітал', null=True)
    country = models.ForeignKey(Country, max_length=60, on_delete=models.CASCADE, null=True,
                                verbose_name='країна')
    address = models.CharField('адреса', max_length=1000, null=True)
    status = models.ForeignKey(Status, on_delete=models.CASCADE, null=True, verbose_name='статус')
    bylaw = models.ForeignKey(Bylaw, on_delete=models.CASCADE, null=True, verbose_name='статут')
    registration_date = models.DateField('дата реєстрації', null=True)
    registration_info = models.CharField('реєстраційні дані', max_length=450, null=True)
    contact_info = models.CharField('контакти', max_length=310, null=True)
    authority = models.ForeignKey(Authority, on_delete=models.CASCADE, null=True,
                                  verbose_name='орган реєстрації')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True,
                               verbose_name='є підрозділом компанії/організації')
    antac_id = models.PositiveIntegerField("id from ANTAC`s DB", unique=True,
                                           db_index=True, null=True, default=None, blank=True)
    from_antac_only = models.BooleanField(null=True)
    source = models.CharField('джерело даних', max_length=5, choices=SOURCES, null=True,
                              blank=True, default=None)
    code = models.CharField(max_length=510, db_index=True)
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
        verbose_name = 'компанія/організація'
        index_together = [
            ('edrpou', 'source')
        ]


class Assignee(DataOceanModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='assignees',
                                verbose_name='є правонаступником')
    name = models.CharField('правонаступник', max_length=610, null=True)
    edrpou = models.CharField('код ЄДРПОУ', max_length=11, null=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'правонаступник'
        verbose_name_plural = 'правонаступники'


class BancruptcyReadjustment(DataOceanModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE,
                                related_name='bancruptcy_readjustment')
    op_date = models.DateField(null=True)
    reason = models.TextField('підстава', null=True)
    sbj_state = models.CharField(max_length=345, null=True)
    head_name = models.CharField(max_length=515, null=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.sbj_state


class CompanyDetail(DataOceanModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='company_detail')
    founding_document_number = models.CharField(max_length=375, null=True)
    executive_power = models.CharField(max_length=390, null=True)
    superior_management = models.CharField(max_length=620, null=True)
    managing_paper = models.CharField(max_length=360, null=True)
    terminated_info = models.CharField(max_length=600, null=True)
    termination_cancel_info = models.CharField(max_length=570, null=True)
    vp_dates = models.TextField(null=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'додаткові дані'


class CompanyToKved(DataOceanModel):  # constraint for only only one truth in primary field
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='kveds')
    kved = models.ForeignKey(Kved, on_delete=models.CASCADE, verbose_name='КВЕД')
    primary_kved = models.BooleanField('зазначений як основний', default=False)
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'КВЕДи компанії'

    def __str__(self):
        return f"{self.kved} (зазначений як основний)" if self.primary_kved else f"{self.kved}"


class ExchangeDataCompany(DataOceanModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='exchange_data')
    authority = models.ForeignKey(Authority, on_delete=models.CASCADE,
                                  verbose_name='орган реєстрації')
    taxpayer_type = models.ForeignKey(TaxpayerType, on_delete=models.CASCADE, null=True)
    start_date = models.DateField(null=True)
    start_number = models.CharField(max_length=555, null=True)
    end_date = models.DateField(null=True)
    end_number = models.CharField(max_length=555, null=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.authority.name


class Founder(DataOceanModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='founders',
                                verbose_name='є засновником компанії/організації')
    info = models.CharField('наявні дані', max_length=2015)
    info_additional = models.CharField('додаткові наявні дані', max_length=2015, null=True)
    info_beneficiary = models.CharField('наявні дані бенефіціара', max_length=2015, null=True)
    name = models.TextField("назва/повне ім'я", db_index=True)
    edrpou = models.CharField('код ЄДРПОУ', max_length=9, null=True, blank=True, default='',
                              db_index=True)
    equity = models.FloatField('участь в статутному капіталі', null=True, blank=True)
    address = models.CharField('адреса', max_length=2015, null=True, blank=True, default='')
    country = models.CharField('держава', max_length=100, null=True, blank=True, default='')
    is_beneficiary = models.BooleanField('є бенефіціаром', blank=True, default=False)
    is_founder = models.BooleanField('є офіційним засновником', blank=True, default=False)
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
        verbose_name = 'засновник'
        verbose_name_plural = 'засновники'


class Predecessor(DataOceanModel):  # constraint for not null in both fields
    name = models.CharField('назва', max_length=500, null=True)
    edrpou = models.CharField('код ЄДРПОУ', max_length=405, null=True)

    class Meta:
        verbose_name = 'попередник'
        verbose_name_plural = 'попередники'


class CompanyToPredecessor(DataOceanModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='predecessors',
                                verbose_name='є попередником організації')
    predecessor = models.ForeignKey(Predecessor, on_delete=models.CASCADE)
    history = HistoricalRecords()

    def __str__(self):
        return self.predecessor.name


class Signer(DataOceanModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='signers')
    name = models.CharField("повне ім'я", max_length=390, null=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'має право підпису'
        verbose_name_plural = 'мають право підпису'


class TerminationStarted(DataOceanModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE,
                                related_name='termination_started')
    op_date = models.DateField(null=True)
    reason = models.TextField('підстава', null=True)
    sbj_state = models.CharField(max_length=530, null=True)
    signer_name = models.CharField(max_length=480, null=True)
    creditor_reg_end_date = models.DateField(null=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.sbj_state
