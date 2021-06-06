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
    nacp_declarant_id = models.PositiveBigIntegerField(
        _('NACP id of the declarant'),
        db_index=True
    )
    submission_date = models.DateField(
        _('submission date'),
        null=True,
        blank=True,
        help_text=_('date of submission of the declaration')
    )
    pep = models.ForeignKey(
        Pep,
        on_delete=models.PROTECT,
        related_name='declarations',
        verbose_name=_('PEP who declares'),
        help_text=_('politically exposed person who declares')
    )
    # looks like this is secret info)
    # date_of_birth = models.DateField(
    #     _('date of birth'),
    #     null=True,
    #     blank=True,
    #     help_text=_('date of birth of the declarant')
    # )
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

    def __str__(self):
        return f'declaration of {self.pep} for {self.year} year'


class Liability(DataOceanModel):
    LOAN = 1
    BORROWED_MONEY_BY_ANOTHER_PERSON = 2
    TAX_DEBT = 3
    PENSION_INSURANCE = 4
    INSURANCE = 5
    LEASING = 6
    LOAN_PAYMENTS = 7
    INTEREST_LOAN_PAYMENTS = 8
    OTHER = 10
    LIABILITY_TYPES = (
        (LOAN, _('Loan')),
        (BORROWED_MONEY_BY_ANOTHER_PERSON, _('Money borrowed by another person')),
        (TAX_DEBT, _('Tax debt')),
        (PENSION_INSURANCE, _('Liabilities under pension insurance contract')),
        (INSURANCE, _('Liabilities under insurance contract')),
        (LEASING, _('Liabilities under leasing contract')),
        (LOAN_PAYMENTS, _('loan payments')),
        (INTEREST_LOAN_PAYMENTS, _('interest payments on the loan')),
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
        help_text=_('type of the liability')
    )
    # please, use this field when the type == OTHER
    additional_info = models.TextField(
        _('additional info'),
        blank=True,
        default='',
        help_text=_('additional info about the liability')
    )
    amount = models.FloatField(
        _('amount'),
        help_text=_('amount of the liability')
    )
    loan_rest = models.FloatField(
        _('loan rest'),
        help_text=_('amount of the rest of the loan')
    )
    loan_paid = models.FloatField(
        _('loan paid'),
        help_text=_('amount of the body of the loan that was paid during declaration`s period')
    )
    interest_paid = models.FloatField(
        _('interest paid'),
        help_text=_('amount of the interest of the loan that was paid during declaration`s period')
    )
    currency = models.CharField(
        _('currency'),
        max_length=33,
        blank=True,
        default='',
        help_text=_('currency')
    )
    # another way of storing currency
    # currency = models.PositiveSmallIntegerField(
    #     _('currency'),
    #     choices=CURRENCIES,
    #     help_text=_('currency')
    # )
    date = models.DateField(
        _('date'),
        null=True,
        blank=True,
        help_text=_('liability date')
    )
    bank_from_info = models.CharField(
        _('info about ukrainian registration'),
        max_length=55,
        blank=True,
        default='',
        help_text=_('info about ukrainian registration of the bank')
    )
    bank_name = models.TextField(
        _('name of the bank'),
        max_length=75,
        blank=True,
        default='',
        help_text=_('name of the bank')
    )
    bank_name_eng = models.TextField(
        _('name of the bank in English'),
        max_length=75,
        blank=True,
        default='',
        help_text=_('name of the bank in English ')
    )
    bank_address = models.TextField(
        _('address of the bank'),
        blank=True,
        default='',
        help_text=_('address of the bank')
    )
    bank_registration_number = models.CharField(
        _('registration number of the bank'),
        max_length=25,
        blank=True,
        default='',
        help_text=_('number of registration of the bank')
    )
    bank = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name='lent_money',
        verbose_name=_('bank'),
        null=True,
        blank=True,
        default=None,
        help_text=_('bank or company to whom money is owed')
    )
    guarantee = models.CharField(
        _('loan guarantee'),
        max_length=65,
        blank=True,
        default='',
        help_text=_('loan guarantee')
    )
    guarantee_amount = models.FloatField(
        _('amount'),
        null=True,
        blank=True,
        help_text=_('amount of the loan guarantee')
    )
    guarantee_registration = models.ForeignKey(
        RatuCity,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        default=None,
        related_name='loans_guarantees',
        verbose_name=_('loan guarantee registration'),
        help_text=_('city of registration of the loan guarantee')
    )
    # looks like we cannot get person NACP id here
    # pep_creditor = models.ForeignKey(
    #     Pep,
    #     on_delete=models.PROTECT,
    #     related_name='lent_money',
    #     verbose_name=_('PEP-creditor'),
    #     null=True,
    #     blank=True,
    #     default=None,
    #     help_text=_('politically exposed person to whom money is owed')
    # )
    creditor_from_info = models.CharField(
        _('info about ukrainian registration'),
        max_length=55,
        blank=True,
        default='',
        help_text=_('info about ukrainian registration of the person to whom money is owed')
    )
    creditor_full_name = models.CharField(
        _('creditor'),
        max_length=75,
        blank=True,
        default='',
        help_text='fullname of the person to whom money is owed'
    )
    creditor_full_name_eng = models.CharField(
        _('creditor fullname in English'),
        max_length=75,
        blank=True,
        default='',
        help_text='fullname of the person to whom money is owed in English'
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
    PRECIOUS_METALS = 5
    OTHER = 10
    TYPES = (
        (BANK_ACCOUNT, _('Bank account')),
        (CASH, _('Hard cash')),
        (CONTRIBUTION, _('Contribution to the credit union or investment fund')),
        (LENT_MONEY, _('Money lent to another person')),
        (PRECIOUS_METALS, _('Precious metals')),
        (OTHER, _('Other')),
    )
    # UAH = 1
    # USD = 2
    # EUR = 3
    # GBP = 4
    # NO_INFO_FROM_FAMILY_MEMBER = 20
    # CURRENCIES = (
    #     (UAH, 'UAH'),
    #     (USD, 'USD'),
    #     (EUR, 'EUR'),
    #     (GBP, 'GBP'),
    #     (NO_INFO_FROM_FAMILY_MEMBER, _('Family member did not provide the information')),
    # )
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
    # please, use this field when the type == OTHER
    additional_info = models.TextField(
        _('additional info'),
        blank=True,
        default='',
        help_text=_('additional info about the money')
    )
    # can be no data for cryptocurrency
    amount = models.FloatField(
        _('amount'),
        null=True,
        blank=True,
        help_text=_('amount of money')
    )
    currency = models.CharField(
        _('currency'),
        max_length=33,
        blank=True,
        default='',
        help_text=_('currency')
    )
    # another way of storing currency
    # # maybe use this? https://pypi.org/project/django-exchange/
    # currency = models.PositiveSmallIntegerField(
    #     _('currency'),
    #     choices=CURRENCIES,
    #     help_text=_('currency')
    # )
    bank_from_info = models.CharField(
        _('info about ukrainian registration'),
        max_length=55,
        blank=True,
        default='',
        help_text=_('info about ukrainian registration of the bank')
    )
    bank_name = models.TextField(
        _('name of the bank'),
        max_length=75,
        blank=True,
        default='',
        help_text=_('name of the bank')
    )
    bank_name_eng = models.TextField(
        _('name of the bank in English'),
        max_length=75,
        blank=True,
        default='',
        help_text=_('name of the bank in English ')
    )
    bank_address = models.TextField(
        _('address of the bank'),
        blank=True,
        default='',
        help_text=_('address of the bank')
    )
    bank_registration_number = models.CharField(
        _('registration number of the bank'),
        max_length=25,
        blank=True,
        default='',
        help_text=_('number of registration of the bank')
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
    # TODO: make sure we can delete this fields
    # pep_borrower = models.ForeignKey(
    #     Pep,
    #     on_delete=models.PROTECT,
    #     related_name='borrowed_money',
    #     verbose_name=_('PEP that borrowed money'),
    #     help_text=_('politically exposed person that borrowed money')
    # )
    # non_pep_borrower = models.CharField(
    #     _('borrower'),
    #     max_length=75,
    #     blank=True,
    #     default='',
    #     help_text='full name of the person that borrowed money'
    # )
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
    BUSINESS = 6
    GIFT_IN_CASH = 7
    GIFT = 8
    FEES = 9
    OTHER = 10
    RENTING_PROPERTY = 11
    PENSION = 12
    INSURANCE_PAYMENTS = 13
    SALE_OF_SECURITIES = 14
    PRIZE = 15
    CHARITY = 16
    SALE_OF_PROPERTY = 17
    LEGACY = 18
    PART_TIME_SALARY = 19
    SALE_OF_LUXURIES = 20
    SELF_EMPLOYMENT = 21

    INCOME_TYPES = (
        (SALARY, _('Salary')),
        (INTEREST, _('Interest')),
        (DIVIDENDS, _('Dividends')),
        (PROPERTY_SALE, _('From sale of property')),
        (SECURITIES_SALE, _('From sale of securities or corporate rights')),
        (BUSINESS, _('Business')),
        (GIFT_IN_CASH, _('Gift in cash')),
        (GIFT, _('Gift')),
        (FEES, _('Fees and other payments')),
        (OTHER, _('Other')),
        (RENTING_PROPERTY, _('Income from renting property')),
        (PENSION, _('Pension')),
        (INSURANCE_PAYMENTS, _('Insurance payments')),
        (SALE_OF_SECURITIES, _('Sale of securities and corporate rights')),
        (PRIZE, _('Prize')),
        (CHARITY, _('Charity')),
        (SALE_OF_PROPERTY, _('Sale of property')),
        (LEGACY, _('Legacy')),
        (PART_TIME_SALARY, _('Salary from part-time job')),
        (SALE_OF_LUXURIES, _('Sale of luxuries')),
        (SELF_EMPLOYMENT, _('Self-employment')),

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
    # please, use this field when the type == OTHER
    additional_info = models.TextField(
        _('additional info'),
        blank=True,
        default='',
        help_text=_('additional info about the income')
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
        help_text=_('full name of the person that paid')
    )
    from_info = models.CharField(
        _('info about ukrainian citizenship or registration'),
        max_length=55,
        blank=True,
        default='',
        help_text=_('info about ukrainian citizenship or registration of the person or company that paid')
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
    MORTGAGE_SECURITIES = 3
    COMMODITY_SECURITIES = 4
    DERIVATIVES = 5
    DEBT_SECURITIES = 6
    PRIVATIZATION_SECURITIES = 7
    INVESTMENT_CERTIFICATES = 8
    CHECK = 9
    OTHER = 10
    ITEM_TYPES = (
        (SHARE, _('Share')),
        (CORPORATE_RIGHTS, _('Corporate right')),
        (MORTGAGE_SECURITIES, _('Mortgage securities')),
        (COMMODITY_SECURITIES, _('Commodity securities')),
        (DERIVATIVES, _('Derivatives')),
        (DEBT_SECURITIES, _('Debt securities')),
        (PRIVATIZATION_SECURITIES, _('Privatization securities (vouchers, etc)')),
        (INVESTMENT_CERTIFICATES, _('Investment certificates)')),
        (CHECK, _('Check')),
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
    # please, use this field when the type == OTHER
    additional_info = models.TextField(
        _('additional info'),
        blank=True,
        default='',
        help_text=_('additional info about securities')
    )
    issuer_from_info = models.CharField(
        _('info about ukrainian registration'),
        max_length=55,
        blank=True,
        default='',
        help_text=_('info about ukrainian registration of the issuer of securities')
    )
    issuer_name = models.TextField(
        _('name of the issuer'),
        max_length=75,
        blank=True,
        default='',
        help_text=_('name of the issuer of securities')
    )
    issuer_name_eng = models.TextField(
        _('name of the issuer in English'),
        max_length=75,
        blank=True,
        default='',
        help_text=_('name in English of the issuer of securities')
    )
    issuer_address = models.TextField(
        _('address of the issuer'),
        blank=True,
        default='',
        help_text=_('address of the issuer of securities')
    )
    issuer_registration_number = models.CharField(
        _('registration number of the issuer'),
        max_length=15,
        blank=True,
        default='',
        help_text=_('number of registration of the issuer of securities')
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
    trustee_from_info = models.CharField(
        _('info about ukrainian registration'),
        max_length=55,
        blank=True,
        default='',
        help_text=_('info about ukrainian registration of the trustee of securities')
    )
    trustee_name = models.TextField(
        _('name of the trustee'),
        max_length=75,
        blank=True,
        default='',
        help_text=_('name of the trustee of securities')
    )
    trustee_name_eng = models.TextField(
        _('name of the trustee in English'),
        max_length=75,
        blank=True,
        default='',
        help_text=_('name in English of the trustee of securities')
    )
    trustee_address = models.TextField(
        _('address of the trustee'),
        blank=True,
        default='',
        help_text=_('address of the trustee of securities')
    )
    trustee_registration_number = models.CharField(
        _('registration number of the trustee'),
        max_length=15,
        blank=True,
        default='',
        help_text=_('number of registration of the trustee of securities')
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
    quantity = models.PositiveIntegerField(
        _('quantity'),
        blank=True,
        null=True,
        help_text=_('quantity of securities')
    )
    nominal_value = models.FloatField(
        _('nominal value'),
        blank=True,
        null=True,
        help_text=_('nominal value of securities')
    )


class Vehicle(DataOceanModel):
    CAR = 1
    TRUCK = 2
    MOTORBIKE = 3
    BOAT = 4
    AGRICULTURAL_MACHINERY = 5
    OTHER = 10

    ITEM_TYPES = (
        (CAR, _('Car')),
        (TRUCK, _('Truck')),
        (BOAT, _('Boat')),
        (AGRICULTURAL_MACHINERY, _('Agricultural machinery')),
        (OTHER, _('Other')),
    )
    declaration = models.ForeignKey(
        Declaration,
        on_delete=models.PROTECT,
        related_name='vehicles',
        verbose_name=_('declaration')
    )

    type = models.PositiveSmallIntegerField(
        _('type'),
        choices=ITEM_TYPES,
        help_text=_('type of the vehicle')
    )
    # please, use this field when the type == OTHER
    additional_info = models.TextField(
        _('additional info'),
        blank=True,
        default='',
        help_text=_('additional info about the vehicle')
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
        max_length=75,
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
    is_luxury = models.BooleanField(
        _('is luxury'),
        null=True,
        blank=True,
        default=None,
        help_text=_('is luxury'),
    )
    valuation = models.PositiveIntegerField(
        _('valuation'),
        null=True,
        blank=True,
        help_text=_('valuation')
    )


class LuxuryItem(DataOceanModel):
    ART = 1
    ELECTRONIC_DEVICES = 2
    ANTIQUES = 3
    CLOTHES = 4
    JEWELRY = 5
    OTHER = 10
    ITEM_TYPES = (
        (ART, _('Art')),
        (ELECTRONIC_DEVICES, _('Personal or home electronic devices')),
        (ANTIQUES, _('Antiques')),
        (CLOTHES, _('Clothes')),
        (JEWELRY, _('Jewelry')),
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
    # please, use this field when the type == OTHER
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
    producer = models.TextField(
        _('producer'),
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
    SUMMER_HOUSE = 2
    APARTMENT = 3
    ROOM = 4
    GARAGE = 5
    UNFINISHED_CONSTRUCTION = 6
    LAND = 7
    OFFICE = 8
    OTHER = 10
    PROPERTY_TYPES = (
        (HOUSE, _('House')),
        (SUMMER_HOUSE, _('Summer house')),
        (APARTMENT, _('Apartment')),
        (ROOM, _('Room')),
        (GARAGE, _('Garage')),
        (UNFINISHED_CONSTRUCTION, _('Unfinished construction')),
        (LAND, _('Land')),
        (OFFICE, _('Office')),
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
    # please, use this field when the type == OTHER
    additional_info = models.TextField(
        _('additional info'),
        blank=True,
        default='',
        help_text=_('additional info about the property')
    )
    area = models.FloatField(
        'square',
        null=True,
        blank=True,
        help_text=_('square meters of the property')

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
    BENEFICIAL_OWNERSHIP = 2
    JOINT_OWNERSHIP = 3
    COMMON_PROPERTY = 4
    RENT = 5
    USAGE = 6
    OWNER_IS_ANOTHER_PERSON = 7
    NO_INFO_FROM_FAMILY_MEMBER = 20
    OTHER_USAGE_RIGHT = 10

    RIGHT_TYPES = (
        (OWNERSHIP, _('Ownership')),
        (BENEFICIAL_OWNERSHIP, _('Beneficial ownership')),
        (JOINT_OWNERSHIP, _('Joint ownership')),
        (COMMON_PROPERTY, _('Common property')),
        (RENT, _('Rent')),
        (USAGE, _('Usage')),
        (OTHER_USAGE_RIGHT, _('Other right of usage')),
        (OWNER_IS_ANOTHER_PERSON, _('Owner is another person')),
        (NO_INFO_FROM_FAMILY_MEMBER, _('Family member did not provide the information')),
    )
    type = models.PositiveSmallIntegerField(
        _('type'),
        choices=RIGHT_TYPES,
        help_text=_('type of the right')
    )
    # please, use this field when the type == OTHER_USAGE_RIGHT
    additional_info = models.TextField(
        _('additional info'),
        blank=True,
        default='',
        help_text=_('additional info about the right')
    )
    acquisition_date = models.DateField(
        _('acquisition date'),
        null=True,
        blank=True,
        help_text=_('date of acquisition of the right')
    )
    share = models.FloatField(
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


class VehicleRight(BaseRight):
    car = models.ForeignKey(
        Vehicle,
        on_delete=models.PROTECT,
        related_name='rights',
        verbose_name=_('vehicle_right'),
        help_text=_('right to the vehicle')
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
