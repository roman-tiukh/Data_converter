from django.db import models
from django.utils.translation import gettext_lazy as _

from business_register.models.company_models import Company
from business_register.models.pep_models import Pep
from data_ocean.models import DataOceanModel
from location_register.models.address_models import Country
from location_register.models.ratu_models import RatuCity


class Declaration(DataOceanModel):
    ANNUAL = 1
    BEFORE_RESIGNATION = 2
    AFTER_RESIGNATION = 3
    CANDIDATE = 4
    DECLARATION_TYPES = (
        (ANNUAL, _('annual declaration')),
        (AFTER_RESIGNATION, _('declaration after resignation')),
        (BEFORE_RESIGNATION, _('declaration before resignation')),
        (CANDIDATE, _('declaration of the candidate')),
    )
    type = models.PositiveSmallIntegerField(
        _('type'),
        choices=DECLARATION_TYPES,
        help_text=_('type of the declaration')
    )
    year = models.PositiveSmallIntegerField(
        _('year of the declaration'),
        help_text=_('year of the declaration')
    )
    nacp_declaration_id = models.CharField(
        _('NACP id'),
        max_length=50,
        unique=True,
        db_index=True,
        help_text=_('NACP id of the declaration'),
    )
    nacp_declarant_id = models.PositiveIntegerField(
        _('NACP id of the declarant'),
        db_index=True
    )
    pep = models.ForeignKey(
        Pep,
        on_delete=models.PROTECT,
        related_name='declarations',
        verbose_name=_('PEP who declares'),
        help_text=_('politically exposed person who declares')
    )
    date_of_birth = models.DateField(
        _('date of birth'),
        null=True,
        blank=True,
        help_text=_('date of birth of the declarant')
    )
    city_of_registration = models.ForeignKey(
        RatuCity,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        default=None,
        related_name='declared_pep_registration',
        verbose_name=_('city of registration'),
        help_text=_('city where the PEP is registered')
    )
    city_of_residence = models.ForeignKey(
        RatuCity,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        default=None,
        related_name='declared_pep_residence',
        verbose_name=_('city of residence'),
        help_text=_('city where the PEP lives')
    )
    last_job_title = models.TextField(
        _('last job title'),
        blank=True,
        default='',
        help_text=_('title of the last job of the declarant')
    )
    last_employer = models.TextField(
        _('last employer'),
        blank=True,
        default='',
        help_text=_('last employer of the declarant')
    )
    spouse = models.ForeignKey(
        Pep,
        null=True,
        blank=True,
        default=None,
        on_delete=models.PROTECT,
        related_name='spouse',
        verbose_name=_('spouse'),
        help_text=_('spouse of the declarant')
    )
    beneficiary_of = models.ManyToManyField(
        Company,
        related_name='beneficiary',
        verbose_name=_('beneficiary of'),
        help_text=_('beneficiary of company')
    )


class Liability(DataOceanModel):
    LOAN = 1
    OTHER = 2
    LIABILITY_TYPES = (
        (LOAN, _('Loan')),
        (OTHER, _('Other')),
    )
    CURRENCIES = (
    )
    declaration = models.ForeignKey(
        Declaration,
        on_delete=models.PROTECT,
        related_name='liabilities',
        verbose_name=_('declaration')
    )
    type = models.PositiveSmallIntegerField(
        _('type'),
        choices=LIABILITY_TYPES,
        help_text=_('type of liability')
    )
    amount = models.PositiveIntegerField(
        _('amount'),
        help_text=_('amount of liability')
    )
    # maybe use this? https://pypi.org/project/django-exchange/
    currency = models.PositiveSmallIntegerField(
        _('currency'),
        choices=CURRENCIES,
        help_text=_('currency')
    )
    bank_creditor = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name='lent_money',
        verbose_name=_('bank'),
        null=True,
        blank=True,
        default=None,
        help_text=_('bank or company to whom money is owed')
    )
    pep_creditor = models.ForeignKey(
        Pep,
        on_delete=models.PROTECT,
        related_name='lent_money',
        verbose_name=_('PEP-creditor'),
        null=True,
        blank=True,
        default=None,
        help_text=_('politically exposed person to whom money is owed')
    )
    non_pep_creditor = models.CharField(
        _('creditor'),
        max_length=75,
        blank=True,
        default='',
        help_text='person to whom money is owed'
    )
    owner = models.ForeignKey(
        Pep,
        on_delete=models.PROTECT,
        related_name='liabilities',
        verbose_name=_('PEP that has the liability'),
        help_text=_('politically exposed person that has the liability')
    )

# Monetary assets
class Money(DataOceanModel):
    BANK_ACCOUNT = 1
    CASH = 2
    CONTRIBUTION = 3
    LENT_MONEY = 4
    TYPES = (
        (BANK_ACCOUNT, _('Bank account')),
        (CASH, _('Hard cash')),
        (CONTRIBUTION, _('Contribution to the credit union or investment fund')),
        (LENT_MONEY, _('Money lent to another person')),
    )
    CURRENCIES = (
    )
    declaration = models.ForeignKey(
        Declaration,
        on_delete=models.PROTECT,
        related_name='money',
        verbose_name=_('declaration')
    )
    type = models.PositiveSmallIntegerField(
        _('type'),
        choices=TYPES,
        help_text=_('type')
    )
    # can be no data for cryptocurrency
    amount = models.PositiveIntegerField(
        _('amount'),
        null=True,
        blank=True,
        help_text=_('amount of money')
    )
    # maybe use this? https://pypi.org/project/django-exchange/
    currency = models.PositiveSmallIntegerField(
        _('currency'),
        choices=CURRENCIES,
        help_text=_('currency')
    )
    bank = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name='money_in_banks',
        null=True,
        blank=True,
        default=None,
        verbose_name=_('bank'),
        help_text=_('bank, credit union or investment fund where the money is stored')
    )
    pep_borrower = models.ForeignKey(
        Pep,
        on_delete=models.PROTECT,
        related_name='borrowed_money',
        verbose_name=_('PEP that borrowed money'),
        help_text=_('politically exposed person that borrowed money')
    )
    non_pep_borrower = models.CharField(
        _('borrower'),
        max_length=75,
        blank=True,
        default='',
        help_text='full name of the person that borrowed money'
    )
    owner = models.ForeignKey(
        Pep,
        on_delete=models.PROTECT,
        related_name='money',
        verbose_name=_('owner'),
        help_text=_('owner of money')
    )


class Income(DataOceanModel):
    SALARY = 1
    INTEREST = 2
    DIVIDENDS = 3
    PROPERTY_SALE = 4
    SECURITIES_SALE = 5
    OTHER = 6
    INCOME_TYPES = (
        (SALARY, _('Salary')),
        (INTEREST, _('Interest')),
        (DIVIDENDS, _('Dividends')),
        (PROPERTY_SALE, _('From sale of property')),
        (SECURITIES_SALE, _('From sale of securities or corporate rights')),
        (OTHER, _('Other')),
    )
    declaration = models.ForeignKey(
        Declaration,
        on_delete=models.PROTECT,
        related_name='income',
        verbose_name=_('declaration')
    )
    type = models.PositiveSmallIntegerField(
        _('type'),
        choices=INCOME_TYPES,
        help_text=_('type of income')
    )
    amount = models.PositiveIntegerField(
        _('amount'),
        help_text=_('amount of income')
    )
    paid_by_company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name='paid_to',
        null=True,
        blank=True,
        default=None,
        verbose_name=_('paid by'),
        help_text=_('company or organisation that paid')
    )
    paid_by_person = models.CharField(
        _('paid by person'),
        max_length=75,
        blank=True,
        default='',
        help_text='full name of the person that paid'
    )
    recipient = models.ForeignKey(
        Pep,
        on_delete=models.PROTECT,
        related_name='incomes',
        verbose_name=_('recipient'),
        help_text=_('person that got income')
    )


class Securities(DataOceanModel):
    SHARE = 1
    CORPORATE_RIGHTS = 2
    OTHER = 3
    ITEM_TYPES = (
        (SHARE, _('Share')),
        (CORPORATE_RIGHTS, _('Corporate right')),
        (OTHER, _('Other')),
    )
    declaration = models.ForeignKey(
        Declaration,
        on_delete=models.PROTECT,
        related_name='securities',
        verbose_name=_('declaration')
    )
    type = models.PositiveSmallIntegerField(
        _('type'),
        choices=ITEM_TYPES,
        help_text=_('type of securities')
    )
    issuer = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name='shares_from_declarations',
        null=True,
        blank=True,
        default=None,
        verbose_name=_('issuer'),
        help_text=_('issuer of securities')
    )
    trustee = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name='shares_in_trust',
        null=True,
        blank=True,
        default=None,
        verbose_name=_('trustee'),
        help_text=_('trustee of securities')
    )
    # quantity
    amount = models.PositiveIntegerField(
        _('amount'),
        blank=True,
        null=True,
        help_text=_('amount of securities')
    )
    nominal_value = models.PositiveIntegerField(
        _('nominal value'),
        blank=True,
        null=True,
        help_text=_('nominal value of securities')
    )
    valuation = models.PositiveIntegerField(
        _('valuation'),
        blank=True,
        null=True,
        help_text=_('valuation')
    )

# Vehicle
class Car(DataOceanModel):
    CAR = 1
    TRUCK = 2
    ITEM_TYPES = (
        (CAR, _('Car')),
        (TRUCK, _('Truck')),
    )
    declaration = models.ForeignKey(
        Declaration,
        on_delete=models.PROTECT,
        related_name='cars',
        verbose_name=_('declaration')
    )

    type = models.PositiveSmallIntegerField(
        _('type'),
        choices=ITEM_TYPES,
        help_text=_('type of the car')
    )
    is_luxury = models.BooleanField(
        _('is luxury'),
        null=True,
        blank=True,
        default=None,
        help_text=_('is luxury'),
    )
    brand = models.CharField(
        _('brand'),
        max_length=40,
        blank=True,
        default='',
        help_text=_('brand')
    )
    model = models.CharField(
        _('model'),
        max_length=20,
        blank=True,
        default='',
        help_text=_('model')
    )
    year = models.PositiveSmallIntegerField(
        _('year of manufacture'),
        null=True,
        blank=True,
        help_text=_('year of manufacture')
    )
    valuation = models.PositiveIntegerField(
        _('valuation'),
        null=True,
        blank=True,
        help_text=_('valuation')
    )


class LuxuryItem(DataOceanModel):
    ART = 1
    OTHER = 2
    ITEM_TYPES = (
        (ART, _('Art')),
        (OTHER, _('Other')),
    )
    declaration = models.ForeignKey(
        Declaration,
        on_delete=models.PROTECT,
        related_name='luxuries',
        verbose_name=_('declaration')
    )
    type = models.PositiveSmallIntegerField(
        _('type'),
        choices=ITEM_TYPES,
        help_text=_('type of the item')
    )
    # add about the type
    additional_info = models.TextField(
        _('additional info'),
        blank=True,
        default='',
        help_text=_('additional info about the item')
    )
    acquired_before_first_declaration = models.BooleanField(
        _('acquired before first declaration'),
        null=True,
        blank=True,
        default=None,
        help_text=_('acquired before first declaration'),
    )
    trademark = models.CharField(
        _('trademark'),
        max_length=40,
        blank=True,
        default='',
        help_text=_('trademark of the item')
    )
    producer = models.CharField(
        _('producer'),
        max_length=20,
        blank=True,
        default='',
        help_text=_('producer of the item')
    )
    description = models.TextField(
        _('description'),
        blank=True,
        default='',
        help_text=_('description of the item')
    )
    valuation = models.PositiveIntegerField(
        _('valuation'),
        null=True,
        blank=True,
        help_text=_('valuation of the item')
    )


class Property(DataOceanModel):
    HOUSE = 1
    LAND = 2
    GARAGE = 3
    UNFINISHED_CONSTRUCTION = 4
    OTHER = 5
    PROPERTY_TYPES = (
        (HOUSE, _('House')),
        (LAND, _('Land')),
        (GARAGE, _('Garage')),
        (UNFINISHED_CONSTRUCTION, _('Unfinished construction')),
        (OTHER, _('Other')),
    )
    declaration = models.ForeignKey(
        Declaration,
        on_delete=models.PROTECT,
        related_name='properties',
        verbose_name=_('declaration')
    )
    type = models.PositiveSmallIntegerField(
        _('type'),
        choices=PROPERTY_TYPES,
        help_text=_('type of the property')
    )
    # add about the type
    additional_info = models.TextField(
        _('additional info'),
        blank=True,
        default='',
        help_text=_('additional info about the property')
    )
    # square meters of the property
    area = models.FloatField(
        'square',
        null=True,
        blank=True,
        help_text=_('square of the property in square meters')

    )
    country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        default=None,
        related_name='declared_pep_properties',
        verbose_name=_('country'),
        help_text=_('country where the property is located'))
    city = models.ForeignKey(
        RatuCity,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        default=None,
        related_name='declared_pep_properties',
        verbose_name=_('address'),
        help_text=_('city where the property is located')
    )
    valuation = models.PositiveIntegerField(
        _('valuation'),
        blank=True,
        null=True,
        help_text=_('valuation of the property')
    )


# abstract model for establishing specific ManyToOne rights
class BaseRight(DataOceanModel):
    OWNERSHIP = 1
    JOINT_OWNERSHIP = 2
    RENT = 3
    USAGE = 4
    PROPERTY_TYPES = (
        (OWNERSHIP, _('Ownership')),
        (JOINT_OWNERSHIP, _('Joint ownership')),
        (RENT, _('Rent')),
        (USAGE, _('Usage'))
    )
    type = models.PositiveSmallIntegerField(
        _('type'),
        choices=PROPERTY_TYPES,
        help_text=_('type of the right')
    )
    acquisition_date = models.DateField(
        _('acquisition date'),
        null=True,
        blank=True,
        help_text=_('date of acquisition of the right')
    )
    share = models.PositiveIntegerField(
        _('share of the right'),
        blank=True,
        null=True,
        help_text=_('share of the right')
    )
    pep = models.ForeignKey(
        Pep,
        on_delete=models.PROTECT,
        related_name='%(app_label)s_%(class)s_rights',
        verbose_name=_('PEP that owns the right'),
        blank=True,
        null=True,
        default=None,
        help_text=_('politically exposed person that owns the right')
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name='%(app_label)s_%(class)s_rights',
        verbose_name=_('company'),
        null=True,
        blank=True,
        default=None,
        help_text=_('company or organisation that owns the right')
    )
    # use this if the owner is a person but not PEP
    full_name = models.CharField(
        _('full name'),
        max_length=75,
        blank=True,
        default='',
        help_text='full name of the person that owns the right'
    )
    country_of_citizenship = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        related_name='%(app_label)s_%(class)s_rights',
        verbose_name=_('country of citizenship'),
        null=True,
        blank=True,
        default=None,
        help_text=_('country of citizenship of the owner of the the right'))

    class Meta:
        abstract = True


class SecuritiesRight(BaseRight):
    securities = models.ForeignKey(
        Securities,
        on_delete=models.PROTECT,
        related_name='rights',
        verbose_name=_('securities_right'),
        help_text=_('right to securities')
    )


class CarRight(BaseRight):
    car = models.ForeignKey(
        Car,
        on_delete=models.PROTECT,
        related_name='rights',
        verbose_name=_('car_right'),
        help_text=_('right to the car')
    )


class LuxuryItemRight(BaseRight):
    luxury_item = models.ForeignKey(
        LuxuryItem,
        on_delete=models.PROTECT,
        related_name='rights',
        verbose_name=_('luxury_item_right'),
        help_text=_('right to the luxury item')
    )


class PropertyRight(BaseRight):
    property = models.ForeignKey(
        Property,
        on_delete=models.PROTECT,
        related_name='rights',
        verbose_name=_('property_right'),
        help_text=_('right to the property')
    )
