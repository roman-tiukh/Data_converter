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
        null=True,
        blank=True,
        default=None,
        help_text=_('law used to impose sanctions')
    )

    class Meta:
        verbose_name = _('Sanction type')
        verbose_name_plural = _('Sanction types')


class Sanction(DataOceanModel):
    PERSON = 'p'
    COMPANY = 'c'
    STATE = 's'
    TYPES = (
        (PERSON, _('Person')),
        (COMPANY, _('Company')),
        (STATE, _('State')),
    )
    object_type = models.CharField(
        _('type of object'),
        choices=TYPES,
        max_length=1,
        help_text=_('type of the object under sanctions')
    )
    is_foreign = models.BooleanField(
        _('is foreign'),
        db_index=True,
        help_text=_('is foreign or Ukrainian')
    )
    # ToDo: decide should we delete 10 fields from there that alreagy have in Pep, Company and Country models (
    #  object_name, object_origin_name, date_of_birth, place_of_birth, address, registration_date,
    #  registration_number, position, id_card, taxpayer_number)
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
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        related_name='official_sanctions',
        null=True,
        blank=True,
        default=None,
        verbose_name=_('country'),
        help_text=_('country under this sanction')
    )
    is_confirmed = models.BooleanField(
        _('is_confirmed'),
        default=False,
        help_text=_('identity of the PEP or company under this sanction is confirmed')
    )
    object_name = models.CharField(
        _('object name'),
        max_length=100,
        db_index=True,
        help_text=_('name of of the object under sanctions')
    )
    object_origin_name = models.CharField(
        _('object origin name'),
        max_length=100,
        db_index=True,
        null=True,
        blank=True,
        default=None,
        help_text=_('name of the object under sanctions in the language of the country of origin')
    )
    date_of_birth = models.DateField(
        _('date of birth'),
        null=True,
        blank=True,
        default=None,
        help_text=_('date of birth')
    )
    place_of_birth = models.CharField(
        _('place of birth'),
        max_length=100,
        null=True,
        blank=True,
        default=None,
        help_text=_('place of birth of the person under sanctions')
    )
    address = models.CharField(
        _('address'),
        max_length=100,
        null=True,
        blank=True,
        default=None,
        help_text=_('place of registration or residence of the person or company under sanctions')
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
        null=True,
        blank=True,
        default=None,
        help_text=_('number of registration of the company under sanctions')
    )
    country_of_origin = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        null=True,
        related_name='sanctions_applied_to_residents',
        verbose_name=_('country of origin'),
        help_text=_('country of citizenship/registration of the person or company under sanctions'))
    position = models.CharField(
        _('position'),
        max_length=500,
        null=True,
        blank=True,
        default=None,
        help_text=_('position or professional activity of the person under sanctions'),

    )
    id_card = models.CharField(
        _('id cards info'),
        max_length=180,
        null=True,
        blank=True,
        default=None,
        help_text=_('id cards info of the person under sanctions')
    )
    taxpayer_number = models.CharField(
        _('taxpayer number'),
        max_length=15,
        db_index=True,
        null=True,
        blank=True,
        default=None,
        help_text=_('taxpayer number of the person or company under sanctions')
    )
    types_of_sanctions = models.ManyToManyField(
        SanctionType,
        related_name='objects_of_sanction',
        verbose_name=_('types of sanctions'),
        help_text=_('types of sanctions applied')
    )
    # Maybe, we should established a different model later
    imposed_by = models.CharField(
        _('imposed by'),
        max_length=50,
        help_text=_('institution that imposed sanctions')
    )
    start_date = models.DateField(
        _('start date'),
        help_text=_('date of imposing sanctions')
    )
    end_date = models.DateField(
        _('end date'),
        help_text=_('end date of sanctions'),
    )
    reasoning = models.CharField(
        _('reasoning'),
        max_length=500,
        null=True,
        blank=True,
        default=None,
        help_text=_('reasoning of imposing sanctions')
    )

    class Meta:
        verbose_name = _('Sanction')
        verbose_name_plural = _('Sanctions')
        ordering = ['start_date']
