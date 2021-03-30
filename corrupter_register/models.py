from django.db import models
from django.utils.translation import ugettext_lazy as _
from data_ocean.models import DataOceanModel


class CorruptCodexArticle(DataOceanModel):
    codex_article_id = models.PositiveIntegerField(
        _('codex_article_id'),
        unique=True,
        help_text='Identifier of the article according to which the person was prosecuted.'
    )
    codex_article_name = models.TextField(
        _('codex article name'),
        help_text='The name of the article under which the person was prosecuted.'
    )


class CorruptPunishment(DataOceanModel):
    code = models.PositiveIntegerField(
        _('code'),
        unique=True,
        help_text='0 - court decision, 1 - disciplinary sanction.'
    )
    name = models.CharField(
        _('name'),
        max_length=30,
        help_text='"court decision" and "disciplinary sanction".'
    )


class CorruptEntity(DataOceanModel):
    code = models.PositiveIntegerField(
        _('code'),
        unique=True,
        help_text='0 - an individual, 1 - a legal entity'
    )
    name = models.CharField(
        _('name'),
        max_length=30,
        help_text='"Individual" and "legal entity".'
    )


class Corrupter(DataOceanModel):
    # COURT_DECISION = 'CD'
    # DISCIPLINARY_ACTION = 'DA'
    # PUNISHMENT_TYPES = (
    #     (COURT_DECISION, _('Court decision')),
    #     (DISCIPLINARY_ACTION, _('Disciplinary action'))
    # )
    # INDIVIDUAL = 'I'
    # LEGAL_ENTITY = 'LE'
    # ENTITY_TYPES = (
    #     (INDIVIDUAL, _('Individual entrepreneur')),
    #     (LEGAL_ENTITY, _('Legal entity'))
    # )
    # punishment_type = models.CharField(
    #     _('punishment_type'),
    #     choices=PUNISHMENT_TYPES,
    #     max_length=2,
    #     help_text='Punishment type. Can be \'court decision\' or \'disciplinary action\'.'
    # )
    # entity_type = models.CharField(
    #     _('entity type'),
    #     choices=ENTITY_TYPES,
    #     max_length=2,
    #     help_text='Entity type. Can be \'Individual entrepreneur\' or \'Legal entity\'.'
    # )
    punishment_type = models.ForeignKey(
        CorruptPunishment,
        on_delete=models.CASCADE,
        help_text='Punishment type. Can be \'court decision\' or \'disciplinary action\'.'
    )
    entity_type = models.ForeignKey(
        CorruptEntity,
        on_delete=models.CASCADE,
        help_text='Entity type. Can be \'Individual\' or \'Legal entity\'.'
    )
    last_name = models.CharField(
        _('last name'),
        max_length=30,
        db_index=True,
        null=True,
        help_text='The last name of the individual at the time of the offense.'
    )
    first_name = models.CharField(
        _('first name'),
        max_length=20,
        db_index=True,
        null=True,
        help_text='The name of the individual at the time of the offense.'
    )
    middle_name = models.CharField(
        _('middle name'),
        max_length=25,
        db_index=True,
        null=True,
        help_text='The middle name of the individual at the time of the offense.'
    )
    place_of_work = models.CharField(
        _('place of work'),
        max_length=350,
        null=True,
        help_text='Place of work of an individual at the time of the offense.'
    )
    position = models.CharField(
        _('position'),
        max_length=100,
        null=True,
        help_text='Position of an  individual at the time of the offense.'
    )
    activity_sphere_id = models.PositiveIntegerField(
        _('Id of activity sphere on offense moment'),
        null=True,
        help_text='Identifier of the sphere of activity of an individual at the time of the offense'
    )
    activity_sphere_name = models.CharField(
        _('name of activity sphere'),
        max_length=200,
        null=True,
        help_text='Name of the sphere of activity of an  individual at the time of the offense.'
    )
    addr_post_index = models.CharField(
        _('postcode'),
        max_length=50,
        null=True,
        help_text='Address of registration of a legal entity at the time of the offense: postal code.'
    )
    addr_country_id = models.PositiveIntegerField(
        _('country identifier'),
        null=True,
        help_text='Address of registration of a legal entity at the time of law enforcement: country identifier.'
    )
    addr_country_name = models.CharField(
        _('country'),
        max_length=20,
        null=True,
        help_text='Address of registration of a legal entity at the time of the offense: name of the country.'
    )
    addr_state_id = models.PositiveIntegerField(
        _('the identifier of the region/city of national importance'),
        null=True,
        help_text='The address of registration of the legal entity at the time of the offense: the identifier of '
                  'the region/city of national importance.'
    )
    addr_state_name = models.CharField(
        _('the name of the region/city of national importance'),
        max_length=30,
        null=True,
        help_text='The address of registration of the legal entity at the time of the offense: the name of '
                  'the region/city of national importance'
    )
    addr_str = models.CharField(
        _('full address'),
        max_length=200,
        null=True,
        help_text='The address of registration of the legal entity at the time of the offense: district, town, '
                  'street, house, premises in the form of a line.'
    )
    short_name = models.CharField(
        _('Short name of the legal entity'),
        max_length=20,
        db_index=True,
        null=True,
        help_text='Abbreviated name of the legal entity at the time of the offense.'
    )
    full_name = models.CharField(
        _('full name of the legal entity'),
        max_length=50,
        db_index=True,
        null=True,
        help_text='Full name of the legal entity at the time of the offense.'
    )
    registration_number = models.CharField(
        _('EDRPOU'),
        max_length=15,
        db_index=True,
        null=True,
        help_text='EDRPOU code of the legal entity'
    )
    legal_form_id = models.PositiveIntegerField(
        _('id of legal form'),
        null=True,
        help_text='Identifier of organizational and legal form of ownership of a legal entity.'
    )
    legal_form_name = models.CharField(
        _('name of legal form'),
        max_length=50,
        null=True,
        help_text='Name of the organizational and legal form of ownership of the legal entity.'
    )
    offense_id = models.PositiveIntegerField(
        _('id of offense'),
        null=True,
        help_text='Identifier of the corrupt offense.'
    )
    offense_name = models.TextField(
        _('name of offense'),
        null=True,
        help_text='The name of the composition of the corruption offense / Method of imposing a disciplinary process.'
    )
    punishment = models.TextField(
        _('punishment'),
        default=_('Data are missing.'),
        null=True,
        help_text='The essence of satisfaction of claims / Type of disciplinary action.'
    )
    decree_date = models.DateField(
        _('decree date'),
        null=True,
        help_text='Date in YYYY-MM-DD format. Date of the order on imposition of disciplinary sanction.'
    )
    decree_number = models.CharField(
        _('decree number'),
        max_length=20,
        null=True,
        help_text='The number of the order imposing a disciplinary sanction.'
    )
    court_case_number = models.CharField(
        _('court case number'),
        max_length=20,
        help_text='The number of court case.'
    )
    sentence_date = models.DateField(
        _('sentence date'),
        help_text='Date in YYYY-MM-DD format. Date of court decision.'
    )
    sentence_number = models.CharField(
        _('sentence number'),
        max_length=20,
        help_text='The number of court decision.'
    )
    punishment_start = models.DateField(
        _('punishment start'),
        help_text='Date in YYYY-MM-DD format. Date of entry into force of the court decision.'
    )
    court_id = models.PositiveIntegerField(
        _('court id'),
        help_text='Identifier of court.'
    )
    court_name = models.CharField(
        _('court name'),
        max_length=100,
        help_text='The name of the court.'
    )
    codex_articles = models.ForeignKey(
        CorruptCodexArticle,
        on_delete=models.CASCADE,
        help_text='Articles under which a person is prosecuted.'
    )

    class Meta:
        verbose_name = _('persons who have committed corruption or corruption-related offenses')
        ordering = ['id']
