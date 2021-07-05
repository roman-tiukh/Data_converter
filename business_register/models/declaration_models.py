from django.db import models
from django.utils.translation import gettext_lazy as _

from business_register.models.company_models import Company
from business_register.models.pep_models import Pep
from business_register.pep_scoring.constants import ScoringRuleEnum
from data_ocean.models import DataOceanModel
from location_register.models.address_models import Country
from location_register.models.ratu_models import RatuCity


class Declaration(DataOceanModel):
    ANNUAL = 1
    BEFORE_RESIGNATION = 2
    AFTER_RESIGNATION = 3
    CANDIDATE = 4
    DECLARATION_TYPES = (
        (ANNUAL, 'annual declaration'),
        (AFTER_RESIGNATION, 'declaration after resignation'),
        (BEFORE_RESIGNATION, 'declaration before resignation'),
        (CANDIDATE, 'declaration of the candidate'),
    )
    type = models.PositiveSmallIntegerField(
        'type',
        choices=DECLARATION_TYPES,
        help_text='type of the declaration'
    )
    year = models.PositiveSmallIntegerField(
        'year of the declaration',
        help_text='year of the declaration'
    )
    nacp_declaration_id = models.CharField(
        'NACP id',
        max_length=50,
        unique=True,
        db_index=True,
        help_text='NACP id of the declaration',
    )
    nacp_declarant_id = models.PositiveBigIntegerField(
        'NACP id of the declarant',
        db_index=True
    )
    submission_date = models.DateField(
        'submission date',
        null=True,
        blank=True,
        help_text='date of submission of the declaration'
    )
    pep = models.ForeignKey(
        Pep,
        on_delete=models.PROTECT,
        related_name='declarations',
        verbose_name='PEP who declares',
        help_text='politically exposed person who declares'
    )
    # looks like this is secret info)
    # date_of_birth = models.DateField(
    #     'date of birth',
    #     null=True,
    #     blank=True,
    #     help_text='date of birth of the declarant'
    # )
    city_of_registration = models.ForeignKey(
        RatuCity,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        default=None,
        related_name='declared_pep_registration',
        verbose_name='city of registration',
        help_text='city where the PEP is registered'
    )
    city_of_residence = models.ForeignKey(
        RatuCity,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        default=None,
        related_name='declared_pep_residence',
        verbose_name='city of residence',
        help_text='city where the PEP lives'
    )
    last_job_title = models.TextField(
        'last job title',
        blank=True,
        default='',
        help_text='title of the last job of the declarant'
    )
    last_employer = models.TextField(
        'last employer',
        blank=True,
        default='',
        help_text='last employer of the declarant'
    )
    spouse = models.ForeignKey(
        Pep,
        null=True,
        blank=True,
        default=None,
        on_delete=models.PROTECT,
        related_name='spouse',
        verbose_name='spouse',
        help_text='spouse of the declarant'
    )

    def __str__(self):
        return f'declaration of {self.pep} for {self.year} year'


class NgoParticipation(DataOceanModel):
    MEMBERSHIP = 1
    LEADERSHIP = 2
    PARTICIPATION_TYPES = (
        (MEMBERSHIP, 'Membership'),
        (LEADERSHIP, 'Leadership')
    )

    PROFESSIONAL_UNION = 1
    PUBLIC_ASSOCIATION = 2
    CHARITY = 3
    NGO_TYPES = (
        (PROFESSIONAL_UNION, 'Professional union'),
        (PUBLIC_ASSOCIATION, 'Public association'),
        (CHARITY, 'Charity')
    )

    AUDIT_BODY = 1
    SUPERVISORY_BODY = 2
    GOVERNING_BODY = 3
    BODY_TYPES = (
        (AUDIT_BODY, 'Audit body'),
        (SUPERVISORY_BODY, 'Supervisory body'),
        (GOVERNING_BODY, 'Governing body'),
    )

    declaration = models.ForeignKey(
        Declaration,
        on_delete=models.PROTECT,
        related_name='ngo_participation',
        verbose_name='declaration'
    )
    participation_type = models.PositiveSmallIntegerField(
        'participation type',
        choices=PARTICIPATION_TYPES,
        help_text='type of the participation in the NGO'
    )
    ngo_type = models.PositiveSmallIntegerField(
        'NGO type',
        choices=NGO_TYPES,
        help_text='type of the NGO'
    )
    ngo_name = models.TextField(
        'NGO name',
        blank=True,
        default='',
        help_text='name of the NGO'
    )
    ngo_registration_number = models.CharField(
        'NGO registration number',
        max_length=25,
        blank=True,
        default='',
        help_text='number of registration of the NGO'
    )
    ngo_body_type = models.PositiveSmallIntegerField(
        'NGO body type',
        choices=BODY_TYPES,
        null=True,
        help_text='type of the NGO`s body'
    )
    ngo_body_name = models.TextField(
        'NGO`s body name',
        blank=True,
        default='',
        help_text='name of the NGO`s body'
    )
    ngo = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name='participants_peps',
        verbose_name='NGO',
        null=True,
        blank=True,
        default=None,
        help_text='NGO in which PEP participates'
    )
    pep = models.ForeignKey(
        Pep,
        on_delete=models.PROTECT,
        related_name='ngos',
        verbose_name='PEP that participates in the NGO',
        help_text='politically exposed person that participates in the NGO'
    )


class PartTimeJob(DataOceanModel):
    declaration = models.ForeignKey(
        Declaration,
        on_delete=models.PROTECT,
        related_name='part_time_jobs',
        verbose_name='declaration'
    )
    is_paid = models.BooleanField(
        'is_paid',
        null=True,
        blank=True,
        default=None,
        help_text='is the job paid'
    )
    description = models.TextField(
        'description',
        blank=True,
        default='',
        help_text='description of the PEP`s part-time job'
    )
    employer_from_info = models.CharField(
        'info about ukrainian registration',
        max_length=55,
        blank=True,
        default='',
        help_text='info about ukrainian registration of the employer'
    )
    employer_name = models.TextField(
        'name of the employer',
        blank=True,
        default='',
        help_text='name of the employer'
    )
    employer_name_eng = models.TextField(
        'name of the employer in English',
        blank=True,
        default='',
        help_text='name of the employer in English '
    )
    employer_address = models.TextField(
        'address of the employer',
        blank=True,
        default='',
        help_text='address of the employer'
    )
    employer_registration_number = models.CharField(
        'registration number of the employer',
        max_length=25,
        blank=True,
        default='',
        help_text='number of registration of the employer'
    )
    employer = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name='peps_employees',
        null=True,
        blank=True,
        default=None,
        verbose_name='employer',
        help_text='employer of the PEP for part-time job'
    )
    employer_full_name = models.TextField(
        'employer full name',
        blank=True,
        default='',
        help_text='full name of the person that gave PEP part-time job'
    )


class Transaction(DataOceanModel):
    declaration = models.ForeignKey(
        Declaration,
        on_delete=models.PROTECT,
        related_name='transactions',
        verbose_name='declaration'
    )
    is_money_spent = models.BooleanField(
        'is_money_spent',
        null=True,
        blank=True,
        default=None,
        help_text='whether the money spent during the transaction'
    )
    amount = models.DecimalField(
        'amount',
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='amount of the transaction'
    )
    transaction_object_type = models.TextField(
        'transaction object`s type',
        blank=True,
        default='',
        help_text='type of the object of the transaction'
    )
    transaction_object = models.TextField(
        'transaction`s object',
        blank=True,
        default='',
        help_text='object of the transaction'
    )
    transaction_result = models.TextField(
        'transaction result',
        blank=True,
        default='',
        help_text='result of the transaction'
    )
    date = models.DateField(
        'date',
        null=True,
        blank=True,
        help_text='date of the transaction'
    )
    country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        default=None,
        related_name='declared_pep_transactions',
        verbose_name=_('country'),
        help_text=_('country where the transaction is registered'))
    participant = models.ForeignKey(
        Pep,
        null=True,
        blank=True,
        default=None,
        on_delete=models.PROTECT,
        related_name='transactions',
        verbose_name='PEP that executes the transaction',
        help_text='politically exposed person that executes the transaction'
    )


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
        (LOAN, 'Loan'),
        (BORROWED_MONEY_BY_ANOTHER_PERSON, 'Money borrowed by another person'),
        (TAX_DEBT, 'Tax debt'),
        (PENSION_INSURANCE, 'Liabilities under pension insurance contract'),
        (INSURANCE, 'Liabilities under insurance contract'),
        (LEASING, 'Liabilities under leasing contract'),
        (LOAN_PAYMENTS, 'loan payments'),
        (INTEREST_LOAN_PAYMENTS, 'interest payments on the loan'),
        (OTHER, 'Other'),
    )
    CURRENCIES = (
    )
    declaration = models.ForeignKey(
        Declaration,
        on_delete=models.PROTECT,
        related_name='liabilities',
        verbose_name='declaration'
    )
    type = models.PositiveSmallIntegerField(
        'type',
        choices=LIABILITY_TYPES,
        help_text='type of the liability'
    )
    # please, use this field when the type == OTHER
    additional_info = models.TextField(
        'additional info',
        blank=True,
        default='',
        help_text='additional info about the liability'
    )
    amount = models.DecimalField(
        'amount',
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='amount of the liability'
    )
    loan_rest = models.DecimalField(
        'loan rest',
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='amount of the rest of the loan'
    )
    loan_paid = models.DecimalField(
        'loan paid',
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='amount of the body of the loan that was paid during declaration`s period'
    )
    interest_paid = models.DecimalField(
        'interest paid',
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='amount of the interest of the loan that was paid during declaration`s period'
    )
    currency = models.CharField(
        'currency',
        max_length=33,
        blank=True,
        default='',
        help_text='currency'
    )
    # another way of storing currency
    # currency = models.PositiveSmallIntegerField(
    #     'currency',
    #     choices=CURRENCIES,
    #     help_text='currency'
    # )
    date = models.DateField(
        'date',
        null=True,
        blank=True,
        help_text='liability date'
    )
    bank_from_info = models.CharField(
        'info about ukrainian registration',
        max_length=55,
        blank=True,
        default='',
        help_text='info about ukrainian registration of the bank'
    )
    bank_name = models.TextField(
        'name of the bank',
        max_length=75,
        blank=True,
        default='',
        help_text='name of the bank'
    )
    bank_name_eng = models.TextField(
        'name of the bank in English',
        max_length=75,
        blank=True,
        default='',
        help_text='name of the bank in English '
    )
    bank_address = models.TextField(
        'address of the bank',
        blank=True,
        default='',
        help_text='address of the bank'
    )
    bank_registration_number = models.CharField(
        'registration number of the bank',
        max_length=25,
        blank=True,
        default='',
        help_text='number of registration of the bank'
    )
    bank = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name='lent_money',
        verbose_name='bank',
        null=True,
        blank=True,
        default=None,
        help_text='bank or company to whom money is owed'
    )
    guarantee = models.CharField(
        'loan guarantee',
        max_length=65,
        blank=True,
        default='',
        help_text='loan guarantee'
    )
    guarantee_amount = models.DecimalField(
        'amount',
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='amount of the loan guarantee'
    )
    guarantee_registration = models.ForeignKey(
        RatuCity,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        default=None,
        related_name='loans_guarantees',
        verbose_name='loan guarantee registration',
        help_text='city of registration of the loan guarantee'
    )
    # looks like we cannot get person NACP id here
    # pep_creditor = models.ForeignKey(
    #     Pep,
    #     on_delete=models.PROTECT,
    #     related_name='lent_money',
    #     verbose_name='PEP-creditor',
    #     null=True,
    #     blank=True,
    #     default=None,
    #     help_text='politically exposed person to whom money is owed'
    # )
    creditor_from_info = models.CharField(
        'info about ukrainian registration',
        max_length=55,
        blank=True,
        default='',
        help_text='info about ukrainian registration of the person to whom money is owed'
    )
    creditor_full_name = models.CharField(
        'creditor',
        max_length=75,
        blank=True,
        default='',
        help_text='fullname of the person to whom money is owed'
    )
    creditor_full_name_eng = models.CharField(
        'creditor fullname in English',
        max_length=75,
        blank=True,
        default='',
        help_text='fullname of the person to whom money is owed in English'
    )
    owner = models.ForeignKey(
        Pep,
        on_delete=models.PROTECT,
        related_name='liabilities',
        verbose_name='PEP that has the liability',
        help_text='politically exposed person that has the liability'
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
        (BANK_ACCOUNT, 'Bank account'),
        (CASH, 'Hard cash'),
        (CONTRIBUTION, 'Contribution to the credit union or investment fund'),
        (LENT_MONEY, 'Money lent to another person'),
        (PRECIOUS_METALS, 'Precious metals'),
        (OTHER, 'Other'),
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
    #     (NO_INFO_FROM_FAMILY_MEMBER, 'Family member did not provide the information'),
    # )
    declaration = models.ForeignKey(
        Declaration,
        on_delete=models.PROTECT,
        related_name='money',
        verbose_name='declaration'
    )
    type = models.PositiveSmallIntegerField(
        'type',
        choices=TYPES,
        help_text='type'
    )
    # please, use this field when the type == OTHER
    additional_info = models.TextField(
        'additional info',
        blank=True,
        default='',
        help_text='additional info about the money'
    )
    # can be no data for cryptocurrency
    amount = models.DecimalField(
        'amount',
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='amount of money'
    )
    currency = models.CharField(
        'currency',
        max_length=33,
        blank=True,
        default='',
        help_text='currency'
    )
    # another way of storing currency
    # # maybe use this? https://pypi.org/project/django-exchange/
    # currency = models.PositiveSmallIntegerField(
    #     'currency',
    #     choices=CURRENCIES,
    #     help_text='currency'
    # )
    bank_from_info = models.CharField(
        'info about ukrainian registration',
        max_length=55,
        blank=True,
        default='',
        help_text='info about ukrainian registration of the bank'
    )
    bank_name = models.TextField(
        'name of the bank',
        max_length=75,
        blank=True,
        default='',
        help_text='name of the bank'
    )
    bank_name_eng = models.TextField(
        'name of the bank in English',
        max_length=75,
        blank=True,
        default='',
        help_text='name of the bank in English '
    )
    bank_address = models.TextField(
        'address of the bank',
        blank=True,
        default='',
        help_text='address of the bank'
    )
    bank_registration_number = models.CharField(
        'registration number of the bank',
        max_length=25,
        blank=True,
        default='',
        help_text='number of registration of the bank'
    )
    bank = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name='money_in_banks',
        null=True,
        blank=True,
        default=None,
        verbose_name='bank',
        help_text='bank, credit union or investment fund where the money is stored'
    )
    # TODO: make sure we can delete this fields
    # pep_borrower = models.ForeignKey(
    #     Pep,
    #     on_delete=models.PROTECT,
    #     related_name='borrowed_money',
    #     verbose_name='PEP that borrowed money',
    #     help_text='politically exposed person that borrowed money'
    # )
    # non_pep_borrower = models.CharField(
    #     'borrower',
    #     max_length=75,
    #     blank=True,
    #     default='',
    #     help_text='full name of the person that borrowed money'
    # )
    owner = models.ForeignKey(
        Pep,
        on_delete=models.PROTECT,
        related_name='money',
        verbose_name='owner',
        help_text='owner of money'
    )


class Income(DataOceanModel):
    SALARY = 1
    INTEREST = 2
    DIVIDENDS = 3
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
    ROYALTY = 22

    INCOME_TYPES = (
        (SALARY, 'Salary'),
        (INTEREST, 'Interest'),
        (DIVIDENDS, 'Dividends'),
        (SECURITIES_SALE, 'From sale of securities or corporate rights'),
        (BUSINESS, 'Business'),
        (GIFT_IN_CASH, 'Gift in cash'),
        (GIFT, 'Gift'),
        (FEES, 'Fees and other payments'),
        (OTHER, 'Other'),
        (RENTING_PROPERTY, 'Income from renting property'),
        (PENSION, 'Pension'),
        (INSURANCE_PAYMENTS, 'Insurance payments'),
        (SALE_OF_SECURITIES, 'Sale of securities and corporate rights'),
        (PRIZE, 'Prize'),
        (CHARITY, 'Charity'),
        (SALE_OF_PROPERTY, 'Sale of property'),
        (LEGACY, 'Legacy'),
        (PART_TIME_SALARY, 'Salary from part-time job'),
        (SALE_OF_LUXURIES, 'Sale of luxuries'),
        (SELF_EMPLOYMENT, 'Self-employment'),
        (ROYALTY, 'Royalty'),
    )
    declaration = models.ForeignKey(
        Declaration,
        on_delete=models.PROTECT,
        related_name='incomes',
        verbose_name='declaration'
    )
    type = models.PositiveSmallIntegerField(
        'type',
        choices=INCOME_TYPES,
        help_text='type of income'
    )
    # please, use this field when the type == OTHER
    additional_info = models.TextField(
        'additional info',
        blank=True,
        default='',
        help_text='additional info about the income'
    )
    amount = models.DecimalField(
        'amount',
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        help_text='amount of income'
    )
    paid_by_company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name='paid_to',
        null=True,
        blank=True,
        default=None,
        verbose_name='paid by',
        help_text='company or organisation that paid'
    )
    paid_by_person = models.CharField(
        'paid by person',
        max_length=100,
        blank=True,
        default='',
        help_text='full name of the person that paid'
    )
    from_info = models.CharField(
        'info about ukrainian citizenship or registration',
        max_length=55,
        blank=True,
        default='',
        help_text='info about ukrainian citizenship or registration of the person or company that paid'
    )
    recipient = models.ForeignKey(
        Pep,
        on_delete=models.PROTECT,
        related_name='incomes',
        verbose_name='recipient',
        help_text='person that got income'
    )


class Beneficiary(DataOceanModel):
    declaration = models.ForeignKey(
        Declaration,
        on_delete=models.PROTECT,
        related_name='beneficiaries',
        verbose_name=_('declaration')
    )
    company_name = models.TextField(
        _('name of the company'),
        max_length=75,
        blank=True,
        default='',
        help_text=_('name of the company')
    )
    company_name_eng = models.TextField(
        _('name of the company in English'),
        max_length=75,
        blank=True,
        default='',
        help_text=_('name in English of the company')
    )
    company_type_name = models.TextField(
        _('name of type of the company'),
        blank=True,
        default='',
        help_text=_('name of type of the company')
    )
    country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        default=None,
        related_name='declared_pep_beneficiaries',
        verbose_name=_('country'),
        help_text=_('country where the company is registered'))
    company_phone = models.TextField(
        _('phone number of the company'),
        blank=True,
        default='',
        help_text=_('phone number of the company')
    )
    company_fax = models.TextField(
        _('fax number of the company'),
        blank=True,
        default='',
        help_text=_('fax number of the company')
    )
    company_email = models.TextField(
        _('email of the company'),
        blank=True,
        default='',
        help_text=_('email of the company')
    )
    company_address = models.TextField(
        'address of the company',
        blank=True,
        default='',
        help_text='address of the company'
    )
    company_registration_number = models.CharField(
        _('registration number of the company'),
        max_length=20,
        blank=True,
        default='',
        help_text=_('number of registration of the company')
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name='beneficiaries_from_declarations',
        null=True,
        blank=True,
        default=None,
        verbose_name=_('company'),
        help_text=_('company')
    )
    beneficiary = models.ForeignKey(
        Pep,
        on_delete=models.PROTECT,
        related_name='beneficiary_info',
        null=True,
        blank=True,
        default=None,
        verbose_name='PEP that is beneficiary',
        help_text='politically exposed person that is beneficiary of the company'
    )


class CorporateRights(DataOceanModel):
    declaration = models.ForeignKey(
        Declaration,
        on_delete=models.PROTECT,
        related_name='corporate_rights',
        verbose_name=_('declaration')
    )

    company_name = models.TextField(
        _('name of the company'),
        max_length=75,
        blank=True,
        default='',
        help_text=_('name of the company')
    )
    company_name_eng = models.TextField(
        _('name of the company in English'),
        max_length=75,
        blank=True,
        default='',
        help_text=_('name in English of the company')
    )
    company_type_name = models.TextField(
        _('name of type of the company'),
        blank=True,
        default='',
        help_text=_('name of type of the company')
    )
    company_registration_number = models.CharField(
        _('registration number of the company'),
        max_length=20,
        blank=True,
        default='',
        help_text=_('number of registration of the company')
    )
    country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        default=None,
        related_name='declared_pep_corporate_rights',
        verbose_name=_('country'),
        help_text=_('country where the company is registered'))
    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name='corporate_rights_from_declarations',
        null=True,
        blank=True,
        default=None,
        verbose_name=_('company'),
        help_text=_('company')
    )
    value = models.DecimalField(
        _('value'),
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        help_text=_('value of rights')
    )
    share = models.DecimalField(
        _('share'),
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        help_text=_('company share')
    )
    is_transferred = models.BooleanField(
        _('is transferred'),
        null=True,
        blank=True,
        default=None,
        help_text=_('is corporate rights transferred to another person or company')
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
        (SHARE, 'Share'),
        (CORPORATE_RIGHTS, 'Corporate right'),
        (MORTGAGE_SECURITIES, 'Mortgage securities'),
        (COMMODITY_SECURITIES, 'Commodity securities'),
        (DERIVATIVES, 'Derivatives'),
        (DEBT_SECURITIES, 'Debt securities'),
        (PRIVATIZATION_SECURITIES, 'Privatization securities (vouchers, etc)'),
        (INVESTMENT_CERTIFICATES, 'Investment certificates)'),
        (CHECK, 'Check'),
        (OTHER, 'Other'),
    )
    declaration = models.ForeignKey(
        Declaration,
        on_delete=models.PROTECT,
        related_name='securities',
        verbose_name='declaration'
    )
    type = models.PositiveSmallIntegerField(
        'type',
        choices=ITEM_TYPES,
        help_text='type of securities'
    )
    # please, use this field when the type == OTHER
    additional_info = models.TextField(
        'additional info',
        blank=True,
        default='',
        help_text='additional info about securities'
    )
    issuer_from_info = models.CharField(
        'info about ukrainian registration',
        max_length=55,
        blank=True,
        default='',
        help_text='info about ukrainian registration of the issuer of securities'
    )
    issuer_name = models.TextField(
        'name of the issuer',
        max_length=75,
        blank=True,
        default='',
        help_text='name of the issuer of securities'
    )
    issuer_name_eng = models.TextField(
        'name of the issuer in English',
        max_length=75,
        blank=True,
        default='',
        help_text='name in English of the issuer of securities'
    )
    issuer_address = models.TextField(
        'address of the issuer',
        blank=True,
        default='',
        help_text='address of the issuer of securities'
    )
    issuer_registration_number = models.CharField(
        'registration number of the issuer',
        max_length=20,
        blank=True,
        default='',
        help_text='number of registration of the issuer of securities'
    )
    issuer = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name='shares_from_declarations',
        null=True,
        blank=True,
        default=None,
        verbose_name='issuer',
        help_text='issuer of securities'
    )
    trustee_from_info = models.CharField(
        'info about ukrainian registration',
        max_length=55,
        blank=True,
        default='',
        help_text='info about ukrainian registration of the trustee of securities'
    )
    trustee_name = models.TextField(
        'name of the trustee',
        max_length=75,
        blank=True,
        default='',
        help_text='name of the trustee of securities'
    )
    trustee_name_eng = models.TextField(
        'name of the trustee in English',
        max_length=75,
        blank=True,
        default='',
        help_text='name in English of the trustee of securities'
    )
    trustee_address = models.TextField(
        'address of the trustee',
        blank=True,
        default='',
        help_text='address of the trustee of securities'
    )
    trustee_registration_number = models.CharField(
        'registration number of the trustee',
        max_length=20,
        blank=True,
        default='',
        help_text='number of registration of the trustee of securities'
    )
    trustee = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name='shares_in_trust',
        null=True,
        blank=True,
        default=None,
        verbose_name='trustee',
        help_text='trustee of securities'
    )
    quantity = models.DecimalField(
        'quantity',
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        help_text='quantity of securities'
    )
    nominal_value = models.DecimalField(
        'nominal value',
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        help_text='nominal value of securities'
    )


class Vehicle(DataOceanModel):
    CAR = 1
    TRUCK = 2
    MOTORBIKE = 3
    BOAT = 4
    AGRICULTURAL_MACHINERY = 5
    AIR_MEANS = 6
    OTHER = 10

    ITEM_TYPES = (
        (CAR, 'Car'),
        (TRUCK, 'Truck'),
        (BOAT, 'Boat'),
        (AGRICULTURAL_MACHINERY, 'Agricultural machinery'),
        (AIR_MEANS, _('Air_means')),
        (OTHER, 'Other'),
    )
    declaration = models.ForeignKey(
        Declaration,
        on_delete=models.PROTECT,
        related_name='vehicles',
        verbose_name='declaration'
    )

    type = models.PositiveSmallIntegerField(
        'type',
        choices=ITEM_TYPES,
        help_text='type of the vehicle'
    )
    # please, use this field when the type == OTHER
    additional_info = models.TextField(
        'additional info',
        blank=True,
        default='',
        help_text='additional info about the vehicle'
    )
    brand = models.CharField(
        'brand',
        max_length=80,
        blank=True,
        default='',
        help_text='brand'
    )
    model = models.CharField(
        'model',
        max_length=140,
        blank=True,
        default='',
        help_text='model'
    )
    year = models.PositiveSmallIntegerField(
        'year of manufacture',
        null=True,
        blank=True,
        help_text='year of manufacture'
    )
    is_luxury = models.BooleanField(
        'is luxury',
        null=True,
        blank=True,
        default=None,
        help_text='is luxury',
    )
    valuation = models.PositiveIntegerField(
        'valuation',
        null=True,
        blank=True,
        help_text='valuation'
    )


class LuxuryItem(DataOceanModel):
    ART = 1
    ELECTRONIC_DEVICES = 2
    ANTIQUES = 3
    CLOTHES = 4
    JEWELRY = 5
    OTHER = 10
    ITEM_TYPES = (
        (ART, 'Art'),
        (ELECTRONIC_DEVICES, 'Personal or home electronic devices'),
        (ANTIQUES, 'Antiques'),
        (CLOTHES, 'Clothes'),
        (JEWELRY, 'Jewelry'),
        (OTHER, 'Other'),
    )
    declaration = models.ForeignKey(
        Declaration,
        on_delete=models.PROTECT,
        related_name='luxuries',
        verbose_name='declaration'
    )
    type = models.PositiveSmallIntegerField(
        'type',
        choices=ITEM_TYPES,
        help_text='type of the item'
    )
    # please, use this field when the type == OTHER
    additional_info = models.TextField(
        'additional info',
        blank=True,
        default='',
        help_text='additional info about the item'
    )
    acquired_before_first_declaration = models.BooleanField(
        'acquired before first declaration',
        null=True,
        blank=True,
        default=None,
        help_text='acquired before first declaration',
    )
    trademark = models.CharField(
        'trademark',
        max_length=100,
        blank=True,
        default='',
        help_text='trademark of the item'
    )
    producer = models.TextField(
        'producer',
        blank=True,
        default='',
        help_text='producer of the item'
    )
    description = models.TextField(
        'description',
        blank=True,
        default='',
        help_text='description of the item'
    )
    valuation = models.PositiveIntegerField(
        'valuation',
        null=True,
        blank=True,
        help_text='valuation of the item'
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
        (HOUSE, 'House'),
        (SUMMER_HOUSE, 'Summer house'),
        (APARTMENT, 'Apartment'),
        (ROOM, 'Room'),
        (GARAGE, 'Garage'),
        (UNFINISHED_CONSTRUCTION, 'Unfinished construction'),
        (LAND, 'Land'),
        (OFFICE, 'Office'),
        (OTHER, 'Other'),
    )
    declaration = models.ForeignKey(
        Declaration,
        on_delete=models.PROTECT,
        related_name='properties',
        verbose_name='declaration'
    )
    type = models.PositiveSmallIntegerField(
        'type',
        choices=PROPERTY_TYPES,
        help_text='type of the property'
    )
    # please, use this field when the type == OTHER
    additional_info = models.TextField(
        'additional info',
        blank=True,
        default='',
        help_text='additional info about the property'
    )
    area = models.FloatField(
        'square',
        null=True,
        blank=True,
        help_text='square meters of the property'

    )
    country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        default=None,
        related_name='declared_pep_properties',
        verbose_name='country',
        help_text='country where the property is located')
    city = models.ForeignKey(
        RatuCity,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        default=None,
        related_name='declared_pep_properties',
        verbose_name='address',
        help_text='city where the property is located'
    )
    valuation = models.DecimalField(
        'valuation',
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        help_text='valuation of the property'
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
        (OWNERSHIP, 'Ownership'),
        (BENEFICIAL_OWNERSHIP, 'Beneficial ownership'),
        (JOINT_OWNERSHIP, 'Joint ownership'),
        (COMMON_PROPERTY, 'Common property'),
        (RENT, 'Rent'),
        (USAGE, 'Usage'),
        (OTHER_USAGE_RIGHT, 'Other right of usage'),
        (OWNER_IS_ANOTHER_PERSON, 'Owner is another person'),
        (NO_INFO_FROM_FAMILY_MEMBER, 'Family member did not provide the information'),
    )
    DECLARANT = 1
    FAMILY_MEMBER = 2
    UKRAINE_CITIZEN = 3
    FOREIGN_CITIZEN = 4
    UKRAINE_LEGAL_ENTITY = 5
    FOREIGN_LEGAL_ENTITY = 6
    OWNER_TYPE = (
        (DECLARANT, 'Declarant'),
        (FAMILY_MEMBER, 'Family member'),
        (UKRAINE_CITIZEN, 'Ukraine citizen'),
        (FOREIGN_CITIZEN, 'Foreign citizen'),
        (UKRAINE_LEGAL_ENTITY, 'Legal entity registered in Ukraine'),
        (FOREIGN_LEGAL_ENTITY, 'Legal entity registered abroad'),
    )
    type = models.PositiveSmallIntegerField(
        'type',
        choices=RIGHT_TYPES,
        null=True,
        blank=True,
        help_text='type of the right'
    )
    owner_type = models.PositiveSmallIntegerField(
        'owner type',
        choices=OWNER_TYPE,
        null=True,
        blank=True,
        help_text='type of the owner',
    )
    # please, use this field when the type == OTHER_USAGE_RIGHT
    additional_info = models.TextField(
        'additional info',
        blank=True,
        default='',
        help_text='additional info about the right'
    )
    acquisition_date = models.DateField(
        'acquisition date',
        null=True,
        blank=True,
        help_text='date of acquisition of the right'
    )
    share = models.DecimalField(
        'share of the right',
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        help_text='share of the right'
    )
    pep = models.ForeignKey(
        Pep,
        on_delete=models.PROTECT,
        related_name='%(app_label)s_%(class)s_rights',
        verbose_name='PEP that owns the right',
        blank=True,
        null=True,
        default=None,
        help_text='politically exposed person that owns the right'
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name='%(app_label)s_%(class)s_rights',
        verbose_name='company',
        null=True,
        blank=True,
        default=None,
        help_text='company or organisation that owns the right'
    )
    # use this if the owner is a person but not PEP
    full_name = models.CharField(
        'full name',
        max_length=75,
        blank=True,
        default='',
        help_text='full name of the person that owns the right'
    )
    company_name = models.CharField(
        'company name',
        max_length=200,
        blank=True,
        help_text='name of the company that owns the right'
    )

    class Meta:
        abstract = True


class CorporateRightsRight(BaseRight):
    corporate_rights = models.ForeignKey(
        CorporateRights,
        on_delete=models.PROTECT,
        related_name='rights',
        verbose_name='corporate rights right',
        help_text='right to corporate rights'
    )


class SecuritiesRight(BaseRight):
    securities = models.ForeignKey(
        Securities,
        on_delete=models.PROTECT,
        related_name='rights',
        verbose_name='securities_right',
        help_text='right to securities'
    )


class VehicleRight(BaseRight):
    car = models.ForeignKey(
        Vehicle,
        on_delete=models.PROTECT,
        related_name='rights',
        verbose_name='vehicle_right',
        help_text='right to the vehicle'
    )


class LuxuryItemRight(BaseRight):
    luxury_item = models.ForeignKey(
        LuxuryItem,
        on_delete=models.PROTECT,
        related_name='rights',
        verbose_name='luxury_item_right',
        help_text='right to the luxury item'
    )


class PropertyRight(BaseRight):
    property = models.ForeignKey(
        Property,
        on_delete=models.PROTECT,
        related_name='rights',
        verbose_name='property_right',
        help_text='right to the property'
    )


class PepScoring(DataOceanModel):
    declaration = models.OneToOneField(Declaration, on_delete=models.PROTECT, related_name='scoring')
    pep = models.ForeignKey(Pep, on_delete=models.PROTECT, related_name='scoring')
    rule_id = models.CharField(max_length=10, choices=[(x.name, x.value) for x in ScoringRuleEnum])
    calculation_date = models.DateField()
    score = models.FloatField()
    data = models.JSONField()

    class Meta:
        verbose_name = 'оцінка ризику обгрунтованості активів'
