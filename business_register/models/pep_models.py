from django.db import models
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords

from business_register.models.company_models import Company, Founder
from data_ocean.models import DataOceanModel
from data_ocean.transliteration.utils import transliterate, translate_country_in_string


class Pep(DataOceanModel):
    DIED = 'died'
    RESIGNED = 'resigned'
    LINKED_PEP_DIED = 'linked pep died'
    LINKED_PEP_RESIGNED = 'linked pep resigned'
    LEGISLATION_CHANGED = 'legislation changed'
    COMPANY_STATUS_CHANGED = 'company status changed'
    REASONS = (
        (DIED, _('Is dead')),
        (RESIGNED, _('Resigned or term ended')),
        (LINKED_PEP_DIED, _("Associated PEP is dead")),
        (LINKED_PEP_RESIGNED, _("Associated person is no more PEP")),
        (LEGISLATION_CHANGED, _('Legislation was changed')),
        (COMPANY_STATUS_CHANGED,
         _('Company is no more state')),
    )
    NATIONAL_PEP = 'national PEP'
    FOREIGN_PEP = 'foreign PEP'
    PEP_FROM_INTERNATIONAL_ORGANISATION = 'PEP with political functions in international organization'
    PEP_ASSOCIATED_PERSON = 'associated person with PEP'
    PEP_FAMILY_MEMBER = "member of PEP`s family"
    TYPES = (
        (NATIONAL_PEP, _('National politically exposed person')),
        (FOREIGN_PEP, _('Foreign politically exposed person')),
        (PEP_FROM_INTERNATIONAL_ORGANISATION,
         _('Politically exposed person, having political functions in international organization')),
        (PEP_ASSOCIATED_PERSON, _("Associated person")),
        (PEP_FAMILY_MEMBER, _("Family member")),
    )

    code = models.CharField(max_length=15, unique=True, db_index=True)
    first_name = models.CharField(
        _('first name'), max_length=20, db_index=True,
        help_text='First name of PEP in Ukrainian'
    )
    middle_name = models.CharField(
        _('middle name'), max_length=25, db_index=True,
        help_text='Middle name of PEP in Ukrainian'
    )
    last_name = models.CharField(
        _('surname'), max_length=30, db_index=True,
        help_text='Last name of PEP in Ukrainian'
    )
    fullname = models.CharField(
        _("full name"), max_length=75, db_index=True,
        help_text='Full name "last name first name middle name" in Ukrainian.'
    )
    fullname_en = models.CharField(
        _("full name in English"), max_length=75, default='',
        help_text='Full name "last name first name middle name" in English.'
    )
    fullname_transcriptions_eng = models.TextField(
        _('options for writing the full name'), db_index=True,
        help_text='Full name in English transcription.'
    )
    last_job_title = models.CharField(
        _('last position'), max_length=340, null=True, db_index=True,
        help_text='Title of the last job in Ukrainian.'
    )
    last_employer = models.CharField(
        _('last office'), max_length=512, null=True, db_index=True,
        help_text='Last employer in Ukrainian.'
    )
    is_pep = models.BooleanField(
        _('is pep'), default=True,
        help_text='Boolean type. Can be true or false. True - person is politically exposed '
                  'person, false - person is not politically exposed person.'
    )
    related_persons = models.ManyToManyField('self', verbose_name=_("associated persons"),
                                             through='RelatedPersonsLink')
    pep_type = models.CharField(
        _('type'), choices=TYPES, max_length=60, null=True,
        blank=True, db_index=True,
        help_text='Type of politically exposed person. Can be national politically exposed '
                  'person, foreign politically exposed person,  politically exposed person,'
                  ' having political functions in international organization, associated '
                  'person or family member.'
    )
    info = models.TextField(_('additional info'), null=True, help_text='Additional info about pep.')
    sanctions = models.TextField(
        _('known sanctions against the person'),
        null=True,
        help_text='Known sanctions against the person. If its is null, the person has no sanctions against him.'
    )
    criminal_record = models.TextField(
        _('known sentences against the person'),
        null=True,
        help_text='Existing criminal proceeding. If its is null, the person has no sentences against him.'
    )
    assets_info = models.TextField(_('assets info'), null=True, help_text='Info about person`s assets.')
    criminal_proceedings = models.TextField(
        _('known criminal proceedings against the person'),
        null=True,
        help_text='Known criminal proceedings against the person. If its is null, the person has no criminal '
                  'proceedings against him.'
    )
    wanted = models.TextField(
        _('wanted'),
        null=True,
        help_text='Information on being wanted. If its null, the person is not on the wanted list.'
    )
    date_of_birth = models.CharField(
        _('date of birth'), max_length=10, null=True, db_index=True,
        help_text='Person`s date of birth in YYYY-MM-DD format.'
    )
    place_of_birth = models.CharField(
        _('place of birth'), max_length=100, null=True,
        help_text='The name of the settlement where the person was born.'
    )
    is_dead = models.BooleanField(
        _('is_dead'), default=False,
        help_text='Boolean type. Can be true or false. True - person is dead, false - person is alive.'
    )
    termination_date = models.DateField(_('PEP status termination date '), null=True,
                                        help_text='PEP status termination date in YYYY-MM-DD format.')
    reason_of_termination = models.CharField(
        _('reason of termination'), choices=REASONS, max_length=125,
        null=True, blank=True,
        help_text='PEP status reason of termination. Can be "Is dead", "Resigned or term ended", "Associated PEP is'
                  ' dead", "Legislation was changed", "Company is no more state" or null.'
    )
    source_id = models.PositiveIntegerField(
        _("id from ANTACs DB"), unique=True, null=True, blank=True
    )
    nacp_id = models.PositiveBigIntegerField(
        _('id from NACP'),
        unique=True,
        null=True,
        blank=True,
        help_text=_('id from the National agency on corruption prevention')
    )
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

    @property
    def pep_org_ua_link(self):
        return 'https://pep.org.ua/uk/person/' + str(self.source_id)

    @property
    def place_of_birth_en(self):
        if self.place_of_birth:
            return transliterate(translate_country_in_string(self.place_of_birth))
        else:
            return None

    class Meta:
        indexes = [
            models.Index(fields=['updated_at']),
        ]
        verbose_name = _('politically exposed person')
        verbose_name_plural = _('politically exposed persons')
        ordering = ['id']

    def __str__(self):
        return self.fullname


class RelatedPersonsLink(DataOceanModel):
    FAMILY = 'family'
    BUSINESS = 'business'
    PERSONAL = 'personal'
    CATEGORIES = (
        (FAMILY, _('Family')),
        (BUSINESS, _('Business')),
        (PERSONAL, _('Personal')),
    )

    from_person = models.ForeignKey(
        Pep, on_delete=models.CASCADE,
        verbose_name=_('associated person'),
        related_name='from_person_links',
        help_text='From which person the connection is established.'
    )
    to_person = models.ForeignKey(
        Pep, on_delete=models.CASCADE,
        verbose_name=_("another associated person"),
        related_name='to_person_links',
        help_text='With what person the connection is established.'
    )
    from_person_relationship_type = models.CharField(
        _("connection`s type"),
        max_length=90,
        null=True,
        help_text='The type of relationship with a related person.'
    )
    to_person_relationship_type = models.CharField(
        _("another person`s connection`s type"),
        max_length=90,
        null=True,
        help_text='The type of relationship with a related person.'
    )
    from_person_relationship_type_en = models.CharField(
        _("connection`s type in English"),
        max_length=90,
        null=True,
        help_text='The type of relationship with a related person in English.'
    )
    to_person_relationship_type_en = models.CharField(
        _("another person`s connection`s type in English"),
        max_length=90,
        null=True,
        help_text='The type of relationship with a related person in English.'
    )
    category = models.CharField(
        _("connection`s category"),
        choices=CATEGORIES,
        max_length=20,
        null=True,
        blank=True,
        help_text='The category of the relationship with the related person. Can be: family, business, personal.'
    )
    start_date = models.DateField(
        _("connection`s start date"),
        null=True,
        help_text='Date of the beginning of the relationship.'
    )
    confirmation_date = models.DateField(
        _("connection`s confirmation date"),
        null=True,
        help_text='Date of confirmation of connection in the "Anti-Corruption Action Center" database.'
    )
    end_date = models.DateField(
        _("connection`s end date"),
        null=True,
        help_text='The date the relationship ends.'
    )
    source_id = models.PositiveIntegerField(
        _("id from ANTACs DB"),
        unique=True,
        null=True,
        default=None)

    def __str__(self):
        return f"connection of {self.from_person.fullname} with {self.to_person.fullname}"

    class Meta:
        verbose_name = _("connection with another PEP")
        verbose_name_plural = _("connections with PEPs")
        ordering = ['id']


class CompanyLinkWithPep(DataOceanModel):
    BANK_CUSTOMER = 'bank_customer'
    BY_POSITION = 'by_position'
    OWNER = 'owner'
    MANAGER = 'manager'
    OTHER = 'other'
    CATEGORIES = (
        (BANK_CUSTOMER, _('Bank client')),
        (OWNER, _('Owner')),
        (BY_POSITION, _('By position')),
        (MANAGER, _('Manager')),
        (OTHER, _('Other')),
    )

    company = models.ForeignKey(Company, on_delete=models.CASCADE,
                                related_name='relationships_with_peps',
                                verbose_name=_("associated with PEP company"),
                                help_text='The company associated with this person.')
    pep = models.ForeignKey(Pep, on_delete=models.CASCADE,
                            related_name='related_companies',
                            verbose_name=_("associated with company PEP"))
    category = models.CharField(_("connection`s category"), max_length=15, choices=CATEGORIES, null=True, default=None,
                                blank=True, help_text='Type of connection between the person and this company '
                                                      'Can be: bank_customer, owner, manager, by_position, other.')
    relationship_type = models.CharField(_("connection`s type"), max_length=550, null=True,
                                         help_text='Type of connection between the person and this company')
    relationship_type_en = models.CharField(_("connection`s type in English"), max_length=550, null=True,
                                         help_text='Type of connection between the person and this company in English')
    start_date = models.DateField(_("connection`s start date"), null=True,
                                  help_text='Date of the beginning of the person\'s connection with the company.')
    confirmation_date = models.DateField(_("connection`s confirmation date"), null=True,
                                         help_text='Date of confirmation of connection in the "Anti-Corruption Action '
                                                   'Center" database.')
    end_date = models.DateField(_("connection`s end date"), null=True,
                                help_text='Date of termination of connection between the person and  this company')
    is_state_company = models.BooleanField(null=True,
                                           help_text='Boolean type. If its true - the company is state-owned,'
                                                     'if its false - the company is private.')
    source_id = models.PositiveIntegerField(_("id from ANTACs DB"), unique=True, null=True, default=None)

    class Meta:
        verbose_name = _("company connection with Pep")
        verbose_name_plural = _("company connections with Peps")
        ordering = ['id']

    def __str__(self):
        return f"connection of {self.company.name} with PEP {self.pep.fullname}"
