from datetime import date

from django.contrib.postgres.fields import ArrayField
from django.core.validators import RegexValidator, MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from data_ocean.models import DataOceanModel
from business_register.models.pep_models import Pep
from business_register.models.company_models import Company
from location_register.models.address_models import Country


class SanctionType(DataOceanModel):
    name = models.TextField(
        _('name'),
        unique=True,
        help_text=_('name of the type of sanctions applied')
    )
    law = models.CharField(
        _('law used'),
        max_length=80,
        blank=True,
        default='',
        help_text=_('law used to impose sanctions')
    )

    def relink_duplicates(self, duplicates: list):
        moved_person_sanctions = 0
        moved_company_sanctions = 0
        moved_country_sanctions = 0

        for sanction_type in duplicates:
            for cs in list(sanction_type.companies_under_sanction.all()):
                cs.types_of_sanctions.remove(sanction_type)
                cs.types_of_sanctions.add(self)
                moved_company_sanctions += 1
            for ps in list(sanction_type.persons_under_sanction.all()):
                ps.types_of_sanctions.remove(sanction_type)
                ps.types_of_sanctions.add(self)
                moved_person_sanctions += 1
            for country_sanction in list(sanction_type.countries_under_sanction.all()):
                country_sanction.types_of_sanctions.remove(sanction_type)
                country_sanction.types_of_sanctions.add(self)
                moved_country_sanctions += 1
        return moved_person_sanctions, moved_company_sanctions, moved_country_sanctions

    @classmethod
    def clean_empty(cls):
        def get_exists(model):
            return models.Exists(
                model.types_of_sanctions.through.objects.filter(
                    sanctiontype_id=models.OuterRef('pk'),
                )
            )

        qs = cls.objects.annotate(
            companies_under_sanction__exists=get_exists(CompanySanction),
            persons_under_sanction__exists=get_exists(PersonSanction),
            countries_under_sanction__exists=get_exists(CountrySanction),
        )
        deleted = 0
        for st in qs:
            is_relations_exists = [
                st.companies_under_sanction__exists,
                st.persons_under_sanction__exists,
                st.countries_under_sanction__exists,
            ]
            if not any(is_relations_exists):
                st.delete()
                deleted += 1
        return deleted

    class Meta:
        verbose_name = _('Sanction type')
        verbose_name_plural = _('Sanction types')


class BaseSanction(DataOceanModel):
    start_date = models.DateField(
        _('start date'),
        help_text=_('date of imposing sanctions')
    )
    cancellation_condition = models.TextField(
        _('cancellation condition'),
        blank=True,
        default='',
        help_text=_('condition of the cancellation of sanctions')
    )
    end_date = models.DateField(
        _('end date'),
        null=True,
        blank=True,
        default=None,
        help_text=_('end date of sanctions'),
    )
    reasoning = models.TextField(
        _('reasoning'),
        default='',
        help_text=_('reasoning of imposing sanctions')
    )
    reasoning_date = models.DateField(
        _('reasoning date'),
        default=None,
        null=True,
        help_text=_('date of reasoning of imposing sanctions')
    )
    initial_data = models.TextField(_('initial data'), blank=True, default='')

    class Meta:
        abstract = True


class CountrySanction(BaseSanction):
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        related_name='official_sanctions',
        verbose_name=_('country'),
        help_text=_('country under this sanction')
    )
    types_of_sanctions = models.ManyToManyField(
        SanctionType,
        related_name='countries_under_sanction',
        verbose_name=_('types of sanctions'),
        help_text=_('types of sanctions applied')
    )

    def __str__(self):
        return f'Sanction against {self.country.name} from {self.start_date}'

    class Meta:
        verbose_name = _('Sanction against country')
        verbose_name_plural = _('Sanctions against countries')
        ordering = ['start_date']


class PersonSanction(BaseSanction):
    pep = models.ForeignKey(
        Pep,
        on_delete=models.CASCADE,
        related_name='official_sanctions',
        null=True,
        blank=True,
        default=None,
        verbose_name=_('PEP'),
        help_text=_('politically exposed person under this sanction')
    )
    first_name = models.CharField(
        _('first name'),
        max_length=20,
        help_text='first name of the person under sanctions'
    )
    middle_name = models.CharField(
        _('middle name'),
        max_length=25,
        blank=True,
        default='',
        help_text='middle name of the person under sanctions'
    )
    last_name = models.CharField(
        _('surname'),
        max_length=30,
        help_text='last name of the person under sanctions'
    )
    full_name = models.CharField(
        _('full name'),
        max_length=75,
        help_text='full name of the person under sanctions'
    )
    full_name_original = models.CharField(
        _('full name original transcription'),
        blank=True,
        default='',
        max_length=75,
        help_text='full name of the person under sanctions in the language of the country of origin'
    )
    date_of_birth = models.DateField(
        _('date of birth'),
        null=True,
        blank=True,
        default=None,
        help_text=_('date of birth of the person under sanctions')
    )
    year_of_birth = models.PositiveSmallIntegerField(
        _('year of birth'),
        null=True,
        blank=True,
        validators=[
            MinValueValidator(1800),
            MaxValueValidator(date.today().year),
        ],
    )
    place_of_birth = models.CharField(
        _('place of birth'),
        max_length=100,
        blank=True,
        default='',
        help_text=_('place of birth of the person under sanctions')
    )
    address = models.TextField(
        _('address'),
        blank=True,
        default='',
        help_text=_('place of registration or residence of the person under sanctions')
    )
    countries_of_citizenship = models.ManyToManyField(
        Country,
        related_name='sanctions_against_citizens',
        verbose_name=_('country of citizenship'),
        help_text=_('country of citizenship of the person under sanctions'))
    occupation = models.TextField(
        _('occupation'),
        blank=True,
        default='',
        help_text=_('occupation or professional activity of the person under sanctions'),
    )
    passports = ArrayField(
        base_field=models.CharField(max_length=15, validators=[RegexValidator(regex=r'^[A-ZА-ЯЄЇҐІ0-9]+$')]),
        verbose_name=_('passports'),
        help_text='',
        default=list,
        blank=True,
    )
    id_card = models.TextField(
        _('id cards info'),
        blank=True,
        default='',
        help_text=_('id cards info of the person under sanctions')
    )
    taxpayer_number = models.CharField(
        _('taxpayer number'),
        max_length=15,
        db_index=True,
        blank=True,
        default='',
        help_text=_('taxpayer number of the person under sanctions')
    )
    additional_info = models.TextField(
        _('additional info'),
        blank=True,
        default='',
        help_text=_('additional info about the person under sanctions')
    )
    types_of_sanctions = models.ManyToManyField(
        SanctionType,
        related_name='persons_under_sanction',
        verbose_name=_('types of sanctions'),
        help_text=_('types of sanctions applied')
    )

    def __str__(self):
        return f'Sanction against {self.full_name} from {self.start_date}'

    def save(self, *args, **kwargs):
        if self.date_of_birth:
            self.year_of_birth = self.date_of_birth.year
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _('Sanction against person')
        verbose_name_plural = _('Sanctions against persons')
        ordering = ['start_date']


class CompanySanction(BaseSanction):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='official_sanctions',
        null=True,
        blank=True,
        default=None,
        verbose_name=_('company'),
        help_text=_('company or organisation under this sanction')
    )
    name = models.TextField(
        _('company name'),
        db_index=True,
        help_text=_('name of the company under sanctions')
    )
    name_original = models.TextField(
        _('original transcription of the name'),
        db_index=True,
        blank=True,
        default='',
        help_text=_('original transcription of the company name in the language of the country of registration')
    )
    address = models.TextField(
        _('address'),
        blank=True,
        default='',
        help_text=_('address of registration or the main office of the company under sanctions')
    )
    registration_date = models.DateField(
        _('registration date'),
        null=True,
        blank=True,
        default=None,
        help_text=_('date of registration of the company under sanctions')
    )
    registration_number = models.CharField(
        _('registration number'),
        max_length=15,
        blank=True,
        default='',
        help_text=_('number of registration of the company under sanctions')
    )
    country_of_registration = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        null=True,
        related_name='sanctions_against_companies',
        verbose_name=_('country of registration'),
        help_text=_('country of registration of the company under sanctions'))
    taxpayer_number = models.CharField(
        _('company taxpayer number'),
        max_length=15,
        db_index=True,
        blank=True,
        default='',
        help_text=_('taxpayer number of the company under sanctions')
    )
    additional_info = models.TextField(
        _('additional info'),
        blank=True,
        default='',
        help_text=_('additional info about the company under sanctions')
    )
    types_of_sanctions = models.ManyToManyField(
        SanctionType,
        related_name='companies_under_sanction',
        verbose_name=_('types of sanctions'),
        help_text=_('types of sanctions applied')
    )

    def __str__(self):
        return f'Sanction against {self.name} from {self.start_date}'

    class Meta:
        verbose_name = _('Sanction against company')
        verbose_name_plural = _('Sanctions against companies')
        ordering = ['start_date']
