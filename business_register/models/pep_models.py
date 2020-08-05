from django.db import models
from simple_history.models import HistoricalRecords
from data_ocean.models import DataOceanModel
from business_register.models.company_models import Company


class Pep(DataOceanModel):
    fullname = models.CharField("повне ім'я", max_length=75)
    fullname_eng = models.CharField("повне ім'я англійською", max_length=75)
    fullname_transcriptions_eng = models.CharField('варіанти написання повного імені англійською',
                                                   max_length=475)
    last_job_title = models.CharField('остання посада', max_length=200, null=True)
    last_job_title_eng = models.CharField('остання посада англійською', max_length=200, null=True)
    last_workplace = models.CharField('останнє місце роботи', max_length=512, null=True)
    last_workplace_eng = models.CharField('останнє місце роботи англійською', max_length=512,
                                          null=True)
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
    is_pep = models.BooleanField('є публічним діячем', default=True)
    pep_type = models.CharField('тип публічного діяча', max_length=60, null=True)
    pep_type_eng = models.CharField('тип публічного діяча англійською', max_length=60, null=True)
    url = models.URLField('посилання на профіль публічного діяча', max_length=512)
    is_alive = models.BooleanField('є публічним діячем', default=True)
    termination_date = models.CharField('дата народження', max_length=10, null=True)
    reason_of_termination = models.CharField('причина припинення статусу публічного діяча',
                                             max_length=50, null=True)
    reason_of_termination_eng = models.CharField('причина припинення статусу публічного діяча англійською',
                                                 max_length=50, null=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'публічний діяч'
        ordering = ['id']

    def __str__(self):
        return self.fullname


class PepRelatedPerson(DataOceanModel):
    pep = models.ForeignKey(Pep, on_delete=models.CASCADE, related_name='related_persons',
                            verbose_name="пов'язана з публічним діячем")
    fullname = models.CharField("повне ім'я", max_length=75)
    relationship_type = models.CharField("тип зв'язку із публічним діячем", max_length=60,
                                         null=True)
    is_pep = models.BooleanField('є публічним діячем', null=True)

    class Meta:
        verbose_name = "пов'язана з публічним діячем особа"
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
    office = models.CharField('назва місця роботи під час декларування', max_length=200, null=True)
    office_eng = models.CharField('назва місця роботи під час декларування англійською',
                                  max_length=200, null=True)
    url = models.URLField('посилання на декларацію', max_length=512)
    region = models.CharField('регіон декларування', max_length=100, null=True)
    region_eng = models.CharField('регіон декларування англійською', max_length=100, null=True)

    class Meta:
        verbose_name = 'декларація публічного діяча'
        ordering = ['id']

    def __str__(self):
        return f"декларація публічного діяча {self.pep.fullname} за {self.year} рік"


class CompanyLinkWithPep(DataOceanModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE,
                                related_name='relationships_with_peps',
                                verbose_name="пов'язана з публічним діячем компанія")
    pep = models.ForeignKey(Pep, on_delete=models.CASCADE,
                            verbose_name="пов'язаний з компанією публічний діяч")
    company_name_eng = models.CharField('назва компанії англійською', max_length=500, null=True)
    company_short_name_eng = models.CharField('скорочена назва компанії англійською',
                                              max_length=500, null=True)
    relationship_type = models.CharField("тип зв'язку із публічним діячем", max_length=50,
                                         null=True)
    relationship_type_eng = models.CharField("тип зв'язку із публічним діячем англійською",
                                             max_length=50, null=True)
    start_date = models.DateField("дата виникнення зв'язку із публічним діячем", null=True)
    end_date = models.DateField("дата припинення зв'язку із публічним діячем", null=True)
    confirmation_date = models.DateField("дата підтвердження зв'язку із публічним діячем",
                                         null=True)
    is_state_company = models.BooleanField(null=True)

    class Meta:
        verbose_name = "зв'язок компанії з публічним діячем"
        ordering = ['id']

    def __str__(self):
        return f"зв'язок компанії {self.company.name} з публічним діячем {self.pep.fullname}"
