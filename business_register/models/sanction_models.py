from django.db import models
from django.utils.translation import gettext_lazy as _

from data_ocean.models import DataOceanModel
from business_register.models.pep_models import Pep
from business_register.models.company_models import Company
from location_register.models.address_models import Country


class SanctionType(DataOceanModel):
    name = models.CharField(
        _('name'),
        max_length=500,
        help_text=_('name of the type of sanctions applied')
    )
    law = models.CharField(
        _('law used'),
        max_length=80,
        blank=True,
        default='',
        help_text=_('law used to impose sanctions')
    )

    class Meta:
        verbose_name = _('Sanction type')
        verbose_name_plural = _('Sanction types')


class Sanction(DataOceanModel):
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
    reasoning = models.CharField(
        _('reasoning'),
        max_length=500,
        blank=True,
        default='',
        help_text=_('reasoning of imposing sanctions')
    )

    class Meta:
        abstract = True


class CountrySanction(Sanction):
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

    class Meta:
        verbose_name = _('Sanction against country')
        verbose_name_plural = _('Sanctions against countries')
        ordering = ['start_date']


class PersonSanction(Sanction):
    is_foreign = models.BooleanField(
        _('is foreign'),
        blank=True,
        default=True,
        db_index=True,
        help_text=_('is foreign or Ukrainian')
    )
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
    full_name_original_transcription = models.CharField(
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
    place_of_birth = models.CharField(
        _('place of birth'),
        max_length=100,
        blank=True,
        default='',
        help_text=_('place of birth of the person under sanctions')
    )
    address = models.CharField(
        _('address'),
        max_length=100,
        blank=True,
        default='',
        help_text=_('place of registration or residence of the person under sanctions')
    )
    countries_of_citizenship = models.ManyToManyField(
        Country,
        related_name='sanctions_against_citizens',
        verbose_name=_('country of citizenship'),
        help_text=_('country of citizenship of the person under sanctions'))
    occupation = models.CharField(
        _('occupation'),
        max_length=500,
        blank=True,
        default='',
        help_text=_('occupation or professional activity of the person under sanctions'),

    )
    id_card = models.CharField(
        _('id cards info'),
        max_length=180,
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
    types_of_sanctions = models.ManyToManyField(
        SanctionType,
        related_name='persons_under_sanction',
        verbose_name=_('types of sanctions'),
        help_text=_('types of sanctions applied')
    )

    class Meta:
        verbose_name = _('Sanction against person')
        verbose_name_plural = _('Sanctions against persons')
        ordering = ['start_date']


class CompanySanction(Sanction):
    is_foreign = models.BooleanField(
        _('is foreign'),
        blank=True,
        default=True,
        db_index=True,
        help_text=_('is foreign or Ukrainian')
    )
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
    name = models.CharField(
        _('company name'),
        max_length=100,
        db_index=True,
        help_text=_('name of the company under sanctions')
    )
    name_original_transcription = models.CharField(
        _('original transcription of the name'),
        max_length=100,
        db_index=True,
        blank=True,
        default='',
        help_text=_('original transcription of the company name in the language of the country of registration')
    )
    address = models.CharField(
        _('address'),
        max_length=100,
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
        max_length=8,
        db_index=True,
        blank=True,
        default='',
        help_text=_('taxpayer number of the company under sanctions')
    )
    types_of_sanctions = models.ManyToManyField(
        SanctionType,
        related_name='companies_under_sanction',
        verbose_name=_('types of sanctions'),
        help_text=_('types of sanctions applied')
    )

    class Meta:
        verbose_name = _('Sanction against company')
        verbose_name_plural = _('Sanctions against companies')
        ordering = ['start_date']
