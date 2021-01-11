from django.db import models
from simple_history.models import HistoricalRecords

from business_register.models.company_models import Company, Founder
from data_ocean.models import DataOceanModel


class Pep(DataOceanModel):
    DIED = 'died'
    RESIGNED = 'resigned'
    LINKED_PEP_DIED = 'linked pep died'
    LINKED_PEP_RESIGNED = 'linked pep resigned'
    LEGISLATION_CHANGED = 'legislation changed'
    COMPANY_STATUS_CHANGED = 'company status changed'
    REASONS = (
        (DIED, 'Помер'),
        (RESIGNED, 'Звільнився або закінчилися повноваження'),
        (LINKED_PEP_DIED, "Пов'язана особа або член сім'ї-публічний діяч помер"),
        (LINKED_PEP_RESIGNED, "Пов'язана особа або член сім'ї-публічний діяч припинив ним бути"),
        (LEGISLATION_CHANGED, 'Змінилося законодавство, що визначає статус публічного діяча'),
        (COMPANY_STATUS_CHANGED, 'Змінилася форма власності компанії, посада в який надавала статус публічного діяча'),
    )
    NATIONAL_PEP = 'national PEP'
    FOREIGN_PEP = 'foreign PEP'
    PEP_FROM_INTERNATIONAL_ORGANISATION = 'PEP with political functions in international organization'
    PEP_ASSOCIATED_PERSON = 'associated person with PEP'
    PEP_FAMILY_MEMBER = "member of PEP`s family"
    TYPES = (
        (NATIONAL_PEP, 'Національний публічний діяч'),
        (FOREIGN_PEP, 'Іноземний публічний діяч'),
        (PEP_FROM_INTERNATIONAL_ORGANISATION, 'Діяч, що виконує політичні функції у міжнародній організації'),
        (PEP_ASSOCIATED_PERSON, "Пов'язана особа"),
        (PEP_FAMILY_MEMBER, "Член сім'ї"),
    )

    code = models.CharField(max_length=15, unique=True, db_index=True)
    first_name = models.CharField("ім'я", max_length=20)
    middle_name = models.CharField('по батькові', max_length=25)
    last_name = models.CharField('прізвище', max_length=30)
    fullname = models.CharField("повне ім'я", max_length=75, db_index=True)
    fullname_eng = models.CharField("повне ім'я англійською", max_length=75, db_index=True)
    fullname_transcriptions_eng = models.TextField('варіанти написання повного імені англійською')
    last_job_title = models.CharField('остання посада', max_length=340, null=True)
    last_job_title_eng = models.CharField('остання посада англійською', max_length=340, null=True)
    last_employer = models.CharField('останнє місце роботи', max_length=512, null=True)
    last_employer_eng = models.CharField('останнє місце роботи англійською', max_length=512,
                                         null=True)
    is_pep = models.BooleanField('є публічним діячем', default=True)
    related_persons = models.ManyToManyField('self', "пов'язані особи",
                                             through='RelatedPersonsLink')
    pep_type = models.CharField('тип публічного діяча', choices=TYPES, max_length=60, null=True, blank=True)
    pep_type_eng = models.CharField('тип публічного діяча англійською', max_length=60, null=True)
    info = models.TextField('додаткова інформація', null=True)
    info_eng = models.TextField('додаткова інформація англійською', null=True)
    sanctions = models.TextField('відомі санкції проти особи', null=True)
    sanctions_eng = models.TextField('відомі санкції проти особи англійською', null=True)
    criminal_record = models.TextField('відомі вироки щодо особи', null=True)
    criminal_record_eng = models.TextField('відомі вироки щодо особи англійською', null=True)
    assets_info = models.TextField('дані про активи', null=True)
    assets_info_eng = models.TextField('дані про активи англійською', null=True)
    criminal_proceedings = models.TextField('відомі кримінальні провадження щодо особи', null=True)
    criminal_proceedings_eng = models.TextField('відомі кримінальні провадження щодо особи англійською',
                                                null=True)
    wanted = models.TextField('перебування в розшуку', null=True)
    wanted_eng = models.TextField('перебування в розшуку англійською', null=True)
    date_of_birth = models.CharField('дата народження', max_length=10, null=True)
    place_of_birth = models.CharField('місце народження', max_length=100, null=True)
    place_of_birth_eng = models.CharField('місце народження англійською', max_length=100,
                                          null=True)

    is_dead = models.BooleanField('помер', default=False)
    termination_date = models.CharField('дата припинення статусу публічного діяча', max_length=10,
                                        null=True)
    reason_of_termination = models.CharField('причина припинення статусу публічного діяча',
                                             choices=REASONS, max_length=125, null=True, blank=True)
    reason_of_termination_eng = models.CharField('причина припинення статусу публічного діяча англійською',
                                                 max_length=125, null=True)
    source_id = models.PositiveIntegerField("id from original ANTAC`s DB", unique=True,
                                            null=True, blank=True)
    history = HistoricalRecords(excluded_fields=['url', 'code'])

    @property
    def check_companies(self):
        pep_name = ' '.join([x for x in [self.last_name, self.first_name, self.middle_name] if x])
        founders_with_pep_name = Founder.objects.filter(
            name__contains=pep_name
        ).select_related('company').distinct('company__edrpou')
        if not len(founders_with_pep_name):
            return []
        possibly_founded_companies = []
        related_companies_id = self.related_companies.values_list('company_id', flat=True)
        for founder in founders_with_pep_name:
            if founder.company_id not in related_companies_id:
                possibly_founded_companies.append(founder.company)
        return possibly_founded_companies

    class Meta:
        verbose_name = 'публічний діяч'
        ordering = ['id']

    def __str__(self):
        return self.fullname


class PepRelatedCountry(DataOceanModel):
    pep = models.ForeignKey(Pep, on_delete=models.CASCADE, related_name='related_countries',
                            verbose_name="пов'язана з публічним діячем")
    name = models.CharField('назва', max_length=50, null=True)
    name_eng = models.CharField('назва англійською', max_length=50, null=True)
    relationship_type = models.CharField("тип зв'язку із публічним діячем", max_length=60,
                                         null=True)

    class Meta:
        verbose_name = "пов'язана з публічним діячем країна"
        ordering = ['id']


class PepDeclaration(DataOceanModel):
    pep = models.ForeignKey(Pep, on_delete=models.CASCADE, related_name='declarations',
                            verbose_name="декларації публічного діяча")
    year = models.SmallIntegerField('рік декларування', null=True)
    income = models.FloatField('задекларований дохід за рік', null=True)
    family_income = models.FloatField('задекларований дохід родини за рік', null=True)
    job_title = models.CharField('посада під час декларування', max_length=200, null=True)
    job_title_eng = models.CharField('посада під час декларування англійською', max_length=200,
                                     null=True)
    employer = models.CharField('назва місця роботи під час декларування', max_length=200, null=True)
    employer_eng = models.CharField('назва місця роботи під час декларування англійською',
                                    max_length=200, null=True)
    url = models.URLField('посилання на декларацію', max_length=512)
    region = models.CharField('регіон декларування', max_length=100, null=True)
    region_eng = models.CharField('регіон декларування англійською', max_length=100, null=True)

    class Meta:
        verbose_name = 'декларація публічного діяча'
        ordering = ['id']

    def __str__(self):
        return f"декларація публічного діяча {self.pep.fullname} за {self.year} рік"


class RelatedPersonsLink(DataOceanModel):
    FAMILY = 'family'
    BUSINESS = 'business'
    PERSONAL = 'personal'
    CATEGORIES = (
        (FAMILY, 'родина'),
        (BUSINESS, 'бізнес'),
        (PERSONAL, "персональний зв'язок"),
    )

    from_person = models.ForeignKey(
        Pep, on_delete=models.CASCADE,
        verbose_name="пов'язана особа",
        related_name='from_person_links'
    )
    to_person = models.ForeignKey(
        Pep, on_delete=models.CASCADE,
        verbose_name="інша пов'язана особа",
        related_name='to_person_links'
    )
    from_person_relationship_type = models.CharField(
        "тип зв'язку першої особи із іншою",
        max_length=90,
        null=True,
    )
    to_person_relationship_type = models.CharField(
        "тип зв'язку іншої особи із першою",
        max_length=90,
        null=True,
    )
    category = models.CharField(
        "категорія зв'язку між особами",
        choices=CATEGORIES,
        max_length=20,
        null=True,
        blank=True
    )
    start_date = models.CharField(
        "дата виникнення зв'язку",
        max_length=12,
        null=True
    )
    confirmation_date = models.CharField(
        "дата підтвердження зв'язку",
        max_length=12,
        null=True
    )
    end_date = models.CharField(
        "дата припинення зв'язку",
        max_length=12,
        null=True
    )

    class Meta:
        verbose_name = "пов'язана з публічним діячем особа"
        ordering = ['id']

    def __str__(self):
        return self.person.fullname


class CompanyLinkWithPep(DataOceanModel):
    BANK_CUSTOMER = 'bank_customer'
    BY_POSITION = 'by_position'
    OWNER = 'owner'
    MANAGER = 'manager'
    OTHER = 'other'
    CATEGORIES = (
        (BANK_CUSTOMER, 'Клієнт банку'),
        (OWNER, 'Власник'),
        (BY_POSITION, 'За позицією'),
        (MANAGER, 'Керівник'),
        (OTHER, 'Інше'),
    )

    company = models.ForeignKey(Company, on_delete=models.CASCADE,
                                related_name='relationships_with_peps',
                                verbose_name="пов'язана з публічним діячем компанія")
    pep = models.ForeignKey(Pep, on_delete=models.CASCADE,
                            related_name='related_companies',
                            verbose_name="пов'язаний з компанією публічний діяч")
    company_name_eng = models.CharField('назва компанії англійською', max_length=500, null=True)
    company_short_name_eng = models.CharField('скорочена назва компанії англійською',
                                              max_length=500, null=True)
    category = models.CharField('категорія', max_length=15, choices=CATEGORIES, null=True, default=None, blank=True)
    relationship_type = models.CharField("тип зв'язку із публічним діячем", max_length=550,
                                         null=True)
    relationship_type_eng = models.CharField("тип зв'язку із публічним діячем англійською",
                                             max_length=550, null=True)
    start_date = models.CharField("дата виникнення зв'язку із публічним діячем", max_length=12,
                                  null=True)
    end_date = models.CharField("дата припинення зв'язку із публічним діячем", max_length=12,
                                null=True)
    confirmation_date = models.CharField("дата підтвердження зв'язку із публічним діячем",
                                         max_length=12, null=True)
    is_state_company = models.BooleanField(null=True)

    class Meta:
        verbose_name = "зв'язок компанії з публічним діячем"
        ordering = ['id']

    def __str__(self):
        return f"зв'язок компанії {self.company.name} з публічним діячем {self.pep.fullname}"
