from django.db import models
from django.utils.translation import ugettext_lazy as _
from data_ocean.models import DataOceanModel
from location_register.models.address_models import Country
from location_register.models.drv_models import ZipCode, DrvStreet, DrvRegion


class CorruptCodexArticle(DataOceanModel):
    codex_article_nazk_id = models.PositiveIntegerField(
        _('codex_article_nazk_id'),
        unique=True,
        help_text='Identifier of the article according to which the person was prosecuted.'
    )
    codex_article_name = models.TextField(
        _('codex article name'),
        help_text='The name of the article under which the person was prosecuted.'
    )

    class Meta:
        verbose_name = 'Codex articles'
        ordering = ['id']


class Court(DataOceanModel):
    court_nazk_id = models.PositiveIntegerField(
        _('court id'),
        unique=True,
        help_text='Identifier of court.'
    )
    court_name = models.CharField(
        _('court name'),
        max_length=100,
        help_text='The name of the court.'
    )

    class Meta:
        verbose_name = 'Court'
        ordering = ['id']


class Offense(DataOceanModel):
    offense_nazk_id = models.PositiveIntegerField(
        _('id of offense'),
        unique=True,
        help_text='Identifier of the corruption offense.'
    )
    offense_name = models.TextField(
        _('name of offense'),
        help_text='The name of the composition of the corruption offense / Method of imposing a disciplinary process.'
    )

    class Meta:
        verbose_name = 'Corruption offense'
        ordering = ['id']


class LegalForm(DataOceanModel):
    legal_form_nazk_id = models.PositiveIntegerField(
        _('id of legal form'),
        unique=True,
        help_text='Identifier of organizational and legal form of ownership of a legal entity.'
    )
    legal_form_name = models.CharField(
        _('name of legal form'),
        max_length=50,
        help_text='Name of the organizational and legal form of ownership of the legal entity.'
    )

    class Meta:
        verbose_name = 'Organizational and legal form of ownership of a legal entity'
        ordering = ['id']


class ActivityShpere(DataOceanModel):
    activity_sphere_nazk_id = models.PositiveIntegerField(
        _('Id of activity sphere on offense moment'),
        unique=True,
        help_text='Identifier of the sphere of activity of an individual at the time of the offense'
    )
    activity_sphere_name = models.CharField(
        _('name of activity sphere'),
        max_length=200,
        help_text='Name of the sphere of activity of an  individual at the time of the offense.'
    )

    class Meta:
        verbose_name = 'Activity sphere'
        ordering = ['id']


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
        (INDIVIDUAL, _('Individual entrepreneur')),
        (LEGAL_ENTITY, _('Legal entity'))
    )
    punishment_type = models.CharField(
        _('punishment_type'),
        choices=PUNISHMENT_TYPES,
        max_length=2,
        null=True,
        blank=True,
        help_text='Punishment type. Can be \'court decision\' or \'disciplinary action\'.'
    )
    entity_type = models.CharField(
        _('entity type'),
        choices=ENTITY_TYPES,
        max_length=2,
        null=True,
        blank=True,
        help_text='Entity type. Can be \'Individual entrepreneur\' or \'Legal entity\'.'
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
    activity_sphere_name = models.ForeignKey(
        ActivityShpere,
        on_delete=models.CASCADE,
    )
    addr_post_index = models.ForeignKey(
        ZipCode,
        on_delete=models.CASCADE,
        verbose_name=_('postcode'),
        null=True,
        blank=True,
        help_text='Address of registration of a legal entity at the time of the offense: postal code.'
    )
    addr_country_name = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text='Address of registration of a legal entity at the time of the offense: name of the country.'
    )
    addr_state_name = models.ForeignKey(
        DrvRegion,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text='The address of registration of the legal entity at the time of the offense: the name of '
                  'the region/city of national importance'
    )
    addr_str = models.ForeignKey(
        DrvStreet,
        on_delete=models.CASCADE,
        verbose_name=_('full address'),
        null=True,
        blank=True,
        help_text='The address of registration of the legal entity at the time of the offense: district, town, '
                  'street, house, premises in the form of a line.'
    )
    short_name = models.CharField(
        _('Short name of the legal entity'),
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
        help_text='EDRPOU code of the legal entity'
    )
    legal_form_name = models.ForeignKey(
        LegalForm,
        on_delete=models.CASCADE,
        verbose_name=_('name of legal form'),
        null=True,
        blank=True
    )
    offense_name = models.ForeignKey(
        Offense,
        verbose_name=_('name of offense'),
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    punishment = models.TextField(
        _('punishment'),
        default=_('Data are missing.'),
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
    court_name = models.ForeignKey(
        Court,
        on_delete=models.CASCADE,
        verbose_name=_('name of the court'),
        null=True,
        blank=True,
    )
    codex_articles = models.ManyToManyField(
        CorruptCodexArticle,
        on_delete=models.CASCADE,
        verbose_name=_('codex articles'),
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _('persons who have committed corruption or corruption-related offenses')
        ordering = ['id']
