from django.db import models
from django.utils.translation import ugettext_lazy as _
from data_ocean.models import DataOceanModel
from location_register.models.address_models import Country
from location_register.models.drv_models import ZipCode, DrvStreet, DrvRegion


class CorruptCodexArticle(DataOceanModel):
    nazk_id = models.PositiveIntegerField(
        'NAZK id',
        unique=True,
        help_text='Identifier of the article according to which the person was prosecuted.'
    )
    name = models.TextField(
        _('name'),
        help_text='The name of the article under which the person was prosecuted.'
    )

    class Meta:
        verbose_name = 'Codex articles'


class Court(DataOceanModel):
    nazk_id = models.PositiveIntegerField(
        'NAZK id',
        unique=True,
        help_text='Identifier of court.'
    )
    name = models.CharField(
        _('name'),
        max_length=100,
        help_text='The name of the court.'
    )

    class Meta:
        verbose_name = _('Court')


class Offense(DataOceanModel):
    nazk_id = models.PositiveIntegerField(
        'NAZK id',
        unique=True,
        help_text='Identifier of the corruption offense.'
    )
    name = models.TextField(
        _('name'),
        help_text='The name of the composition of the corruption offense / Method of imposing a disciplinary process.'
    )

    class Meta:
        verbose_name = _('Corruption offense')


class LegalForm(DataOceanModel):
    nazk_id = models.PositiveIntegerField(
        'NAZK id',
        unique=True,
        help_text='Identifier of organizational and legal form of ownership of a legal entity.'
    )
    name = models.CharField(
        _('name'),
        max_length=50,
        help_text='The name of the organizational and legal form of ownership of the legal entity.'
    )

    class Meta:
        verbose_name = _('Organizational and legal form')


class ActivityShpere(DataOceanModel):
    nazk_id = models.PositiveIntegerField(
        'NAZK id',
        unique=True,
        help_text='Identifier of the sphere of activity of an individual at the time of the offense'
    )
    name = models.CharField(
        _('name'),
        max_length=200,
        help_text='Name of the sphere of activity of an  individual at the time of the offense.'
    )

    class Meta:
        verbose_name = _('Activity sphere')


class CorruptPerson(DataOceanModel):
    COURT_DECISION = 'CD'
    DISCIPLINARY_ACTION = 'DA'
    PUNISHMENT_TYPES = (
        (COURT_DECISION, _('Court decision')),
        (DISCIPLINARY_ACTION, _('Disciplinary action'))
    )
    INDIVIDUAL = 'I'
    LEGAL_ENTITY = 'LE'
    ENTITY_TYPES = (
        (INDIVIDUAL, _('Individual')),
        (LEGAL_ENTITY, _('Legal entity'))
    )
    person_nazk_id = models.PositiveIntegerField(
        'NAZK id',
        unique=True,
        help_text='Identifier of the person in the NAZK database.'
    )
    punishment_type = models.CharField(
        _('punishment type'),
        choices=PUNISHMENT_TYPES,
        max_length=2,
        null=True,
        blank=True,
        help_text='Punishment type. Can be \'Court decision\' or \'Disciplinary action\'.'
    )
    entity_type = models.CharField(
        _('entity type'),
        choices=ENTITY_TYPES,
        max_length=2,
        null=True,
        blank=True,
        help_text='Entity type. Can be \'Individual\' or \'Legal entity\'.'
    )
    last_name = models.CharField(
        _('last name'),
        max_length=30,
        db_index=True,
        null=True,
        blank=True,
        help_text='The last name of the individual at the time of the offense.'
    )
    first_name = models.CharField(
        _('first name'),
        max_length=20,
        db_index=True,
        null=True,
        blank=True,
        help_text='The name of the individual at the time of the offense.'
    )
    middle_name = models.CharField(
        _('middle name'),
        max_length=25,
        db_index=True,
        null=True,
        blank=True,
        help_text='The middle name of the individual at the time of the offense.'
    )
    place_of_work = models.CharField(
        _('place of work'),
        max_length=350,
        null=True,
        blank=True,
        help_text='Place of work of an individual at the time of the offense.'
    )
    position = models.CharField(
        _('position'),
        max_length=100,
        null=True,
        blank=True,
        help_text='Position of an  individual at the time of the offense.'
    )
    activity_sphere = models.ForeignKey(
        ActivityShpere,
        on_delete=models.CASCADE,
        verbose_name=_('activity sphere'),
        null=True,
        blank=True,
        help_text='The sphere of activity of an individual at the time of the offense.'
    )
    addr_post_index = models.CharField(
        _('postcode'),
        max_length=50,
        null=True,
        blank=True,
        help_text='Address of registration of a legal entity at the time of the offense: postal code.'
    )
    addr_country_id = models.PositiveIntegerField(
        _('country identifier'),
        null=True,
        blank=True,
        help_text='Address of registration of a legal entity at the time of law enforcement: country identifier.'
    )
    addr_country_name = models.CharField(
        _('country'),
        max_length=50,
        null=True,
        blank=True,
        help_text='Address of registration of a legal entity at the time of the offense: name of the country.'
    )
    addr_state_id = models.PositiveIntegerField(
        _('the identifier of the region/city'),
        null=True,
        blank=True,
        help_text='The address of registration of the legal entity at the time of the offense: the identifier of '
                  'the region/city of national importance.'
    )
    addr_state_name = models.CharField(
        _('the name of the region/city'),
        max_length=50,
        null=True,
        blank=True,
        help_text='The address of registration of the legal entity at the time of the offense: the name of '
                  'the region/city of national importance'
    )
    addr_str = models.CharField(
        _('full address'),
        max_length=200,
        null=True,
        blank=True,
        help_text='The address of registration of the legal entity at the time of the offense: district, town, '
                  'street, house, premises in the form of a line.'
    )
    short_name = models.CharField(
        _('short name of the legal entity'),
        max_length=20,
        db_index=True,
        null=True,
        blank=True,
        help_text='Abbreviated name of the legal entity at the time of the offense.'
    )
    legal_entity_name = models.CharField(
        _('the name of the legal entity'),
        max_length=50,
        db_index=True,
        null=True,
        blank=True,
        help_text='The name of the legal entity at the time of the offense.'
    )
    registration_number = models.CharField(
        _('EDRPOU'),
        max_length=15,
        db_index=True,
        null=True,
        blank=True,
        help_text='EDRPOU code of the legal entity.'
    )
    legal_form = models.ForeignKey(
        LegalForm,
        on_delete=models.CASCADE,
        verbose_name=_('legal form'),
        null=True,
        blank=True,
        help_text='The organizational and legal form of ownership of the legal entity.',
    )
    offense = models.ForeignKey(
        Offense,
        verbose_name=_('offense'),
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        help_text='The composition of the corruption offense / Method of imposing a disciplinary process.'
    )
    punishment = models.TextField(
        _('punishment'),
        default=_('data are missing.'),
        null=True,
        blank=True,
        help_text='The essence of satisfaction of claims / Type of disciplinary action.'
    )
    decree_date = models.DateField(
        _('decree date'),
        null=True,
        blank=True,
        help_text='Date in YYYY-MM-DD format. Date of the order on imposition of disciplinary sanction.'
    )
    decree_number = models.CharField(
        _('decree number'),
        max_length=20,
        null=True,
        blank=True,
        help_text='The number of the order imposing a disciplinary sanction.'
    )
    court_case_number = models.CharField(
        _('court case number'),
        max_length=20,
        null=True,
        blank=True,
        help_text='The number of court case.'
    )
    sentence_date = models.DateField(
        _('sentence date'),
        null=True,
        blank=True,
        help_text='Date in YYYY-MM-DD format. Date of court decision.'
    )
    sentence_number = models.CharField(
        _('sentence number'),
        max_length=20,
        null=True,
        blank=True,
        help_text='The number of court decision.'
    )
    punishment_start = models.DateField(
        _('punishment start'),
        null=True,
        blank=True,
        help_text='Date in YYYY-MM-DD format. Date of entry into force of the court decision.'
    )
    court = models.ForeignKey(
        Court,
        on_delete=models.CASCADE,
        verbose_name=_('court'),
        null=True,
        blank=True,
        help_text='The court that made the judgment.'
    )
    codex_articles = models.ManyToManyField(
        CorruptCodexArticle,
        verbose_name=_('codex articles'),
        help_text='The article under which the person was prosecuted.'
    )

    class Meta:
        verbose_name = _('Persons who have committed corruption or corruption-related offenses')
