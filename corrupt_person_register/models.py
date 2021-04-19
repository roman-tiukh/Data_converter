from django.db import models
from django.utils.translation import gettext_lazy as _
from data_ocean.models import DataOceanModel


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
        verbose_name = _('Codex articles')


class BaseCorruptPerson(DataOceanModel):
    COURT_DECISION = 'CD'
    DISCIPLINARY_ACTION = 'DA'
    PUNISHMENT_TYPES = (
        (COURT_DECISION, _('Court decision')),
        (DISCIPLINARY_ACTION, _('Disciplinary action'))
    )
    person_id = models.PositiveIntegerField(
        _('the NAZK identifier of person'),
        help_text='identifier of the person in the NAZK database.'
    )
    punishment_type = models.CharField(
        _('punishment type'),
        choices=PUNISHMENT_TYPES,
        max_length=2,
        help_text='Punishment type. Can be \'Court decision\' or \'Disciplinary action\'.'
    )
    offense_id = models.PositiveIntegerField(
        _('the NAZK identifier of offense'),
        null=True,
        blank=True,
        help_text='Identifier of the corruption offense.'
    )
    offense_name = models.TextField(
        _('the name of offense'),
        default='',
        blank=True,
        help_text='The name of the composition of the corruption offense / Method of imposing a disciplinary process.'
    )
    punishment = models.TextField(
        _('punishment'),
        default='',
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
        max_length=100,
        default='',
        blank=True,
        help_text='The number of the order imposing a disciplinary sanction.'
    )
    court_case_number = models.CharField(
        _('court case number'),
        max_length=100,
        default='',
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
        max_length=100,
        default='',
        blank=True,
        help_text='The number of court decision.'
    )
    punishment_start = models.DateField(
        _('punishment start'),
        null=True,
        blank=True,
        help_text='Date in YYYY-MM-DD format. Date of entry into force of the court decision.'
    )
    codex_articles = models.ManyToManyField(
        CorruptCodexArticle,
        verbose_name=_('codex articles'),
        help_text='The article under which the person was prosecuted.'
    )
    court_id = models.PositiveIntegerField(
        _('the NAZK identifier of court'),
        null=True,
        blank=True,
        help_text='Identifier of court.'
    )
    court_name = models.CharField(
        _('the name of court'),
        max_length=500,
        default='',
        blank=True,
        help_text='The name of the court.'
    )

    class Meta:
        abstract = True


class CorruptLegalEntity(BaseCorruptPerson):
    addr_post_index = models.CharField(
        _('postcode'),
        max_length=50,
        default='',
        blank=True,
        help_text='Address of registration of a legal entity at the time of the offense: postal code.'
    )
    addr_country_id = models.PositiveIntegerField(
        _('the NAZK identifier of country'),
        null=True,
        blank=True,
        help_text='Address of registration of a legal entity at the time of law enforcement: country identifier.'
    )
    addr_country_name = models.CharField(
        _('country'),
        max_length=100,
        default='',
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
        max_length=100,
        default='',
        blank=True,
        help_text='The address of registration of the legal entity at the time of the offense: the name of '
                  'the region/city of national importance'
    )
    addr_str = models.CharField(
        _('full address'),
        max_length=300,
        default='',
        blank=True,
        help_text='The address of registration of the legal entity at the time of the offense: district, town, '
                  'street, house, premises in the form of a line.'
    )
    short_name = models.CharField(
        _('short name of the legal entity'),
        max_length=100,
        db_index=True,
        default='',
        blank=True,
        help_text='Abbreviated name of the legal entity at the time of the offense.'
    )
    legal_entity_name = models.CharField(
        _('the name of the legal entity'),
        max_length=500,
        db_index=True,
        default='',
        blank=True,
        help_text='The name of the legal entity at the time of the offense.'
    )
    registration_number = models.CharField(
        _('EDRPOU'),
        max_length=100,
        db_index=True,
        default='',
        blank=True,
        help_text='EDRPOU code of the legal entity.'
    )
    legal_form_id = models.PositiveIntegerField(
        _('the NAZK identifier of legal form'),
        default='',
        blank=True,
        help_text='Identifier of organizational and legal form of ownership of a legal entity.'
    )
    legal_form_name = models.CharField(
        _('the name of legal form'),
        max_length=500,
        default='',
        blank=True,
        help_text='The name of the organizational and legal form of ownership of the legal entity.'
    )

    class Meta:
        verbose_name = _('Legal entity who have committed corruption or corruption-related offenses')


class CorruptIndividual(BaseCorruptPerson):
    last_name = models.CharField(
        _('last name'),
        max_length=50,
        db_index=True,
        default='',
        blank=True,
        help_text='The last name of the individual at the time of the offense.'
    )
    first_name = models.CharField(
        _('first name'),
        max_length=50,
        db_index=True,
        default='',
        blank=True,
        help_text='The name of the individual at the time of the offense.'
    )
    middle_name = models.CharField(
        _('middle name'),
        max_length=50,
        db_index=True,
        default='',
        blank=True,
        help_text='The middle name of the individual at the time of the offense.'
    )
    place_of_work = models.CharField(
        _('place of work'),
        max_length=500,
        default='',
        blank=True,
        help_text='Place of work of an individual at the time of the offense.'
    )
    occupation = models.CharField(
        _('occupation'),
        max_length=500,
        default='',
        blank=True,
        help_text='Position of an  individual at the time of the offense.'
    )
    activity_sphere_id = models.PositiveIntegerField(
        _('the NAZK identifier of activity sphere'),
        null=True,
        blank=True,
        help_text='Identifier of the sphere of activity of an individual at the time of the offense'
    )
    activity_sphere_name = models.CharField(
        _('the name of activity sphere'),
        max_length=500,
        default='',
        blank=True,
        help_text='Name of the sphere of activity of an  individual at the time of the offense.'
    )

    class Meta:
        verbose_name = _('Individual who have committed corruption or corruption-related offenses')
