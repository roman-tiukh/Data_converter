from django.db import models
from django.utils.translation import ugettext_lazy as _

from data_ocean.models import DataOceanModel
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
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        null=True,
        related_name='residents_under_sanctions',
        verbose_name=_('country'),
        help_text='Country of citizenship/registration of the person or company under sanctions')
    position = models.CharField(
        _('position'),
        max_length=500,
        null=True,
        blank=True,
        default=None,
        help_text=_('position or professional activity of the person under sanctions'),

    )
    id_card = models.CharField(
        _('id card info'),
        max_length=100,
        null=True,
        blank=True,
        default=None,
        help_text=_('id card the person under sanctions')
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
    type_of_sanctions = models.ForeignKey(
        SanctionType,
        on_delete=models.CASCADE,
        related_name='objects_of_sanction',
        verbose_name=_('type of sanctions'),
        help_text=_('type of sanctions')
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
