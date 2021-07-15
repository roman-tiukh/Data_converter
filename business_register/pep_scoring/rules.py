from decimal import Decimal
from django.db.models import Sum, Q

from abc import ABC, abstractmethod

from django.utils import timezone
from rest_framework import serializers
from typing import Tuple, Union

from rest_framework.exceptions import ValidationError

from business_register.models.declaration_models import (
    Declaration,
    Property,
    Vehicle,
    VehicleRight,
    Income,
    Money,
    PropertyRight,
    BaseRight,
    PepScoring,
    IntangibleAsset,
    Transaction,
    Beneficiary,
    Liability
)
from business_register.models.pep_models import CompanyLinkWithPep
from business_register.models.company_models import Company
from business_register.models.pep_models import (RelatedPersonsLink, Pep)
from business_register.pep_scoring.rules_registry import register_rule, ScoringRuleEnum
from location_register.models.ratu_models import RatuCity
from data_ocean.utils import convert_to_usd

RESULT_FALSE = 0, {}
UAH = 'UAH'
FIRST_DECLARING_YEAR = 2015

SPOUSE_TYPES = ['дружина', 'чоловік']
GIFT_TYPES = [Income.GIFT_IN_CASH, Income.GIFT]
OWNERSHIP_TYPES = [BaseRight.OWNERSHIP, BaseRight.COMMON_PROPERTY, BaseRight.JOINT_OWNERSHIP]
REAL_ESTATE_TYPES = [
    Property.SUMMER_HOUSE,
    Property.HOUSE,
    Property.APARTMENT,
    Property.ROOM,
    Property.UNFINISHED_CONSTRUCTION
]

ANTAC_BENEFICIARY_TYPES = {
    "Колишній директор, Бенефіціарний власник",
    "Бенефіціарний власник",
    "Колишній засновник, бенефіціар",
    "Бенефіціарний власник",
    "Бенефіціарний власник, Голова наглядової ради",
    "Бенефіціарний власник/співзасновник",
    "Засновник, бенефіціар",
    "бенефіціарний власник",
}


def get_total_USD(data, year):
    total_USD = 0

    if data:
        for currency, amount in data:
            total_USD += convert_to_usd(currency, float(amount), year)
    return total_USD


def get_total_income(declaration_id):
    total_income = 0

    incomes_amount = Income.objects.filter(
        declaration=declaration_id,
        amount__isnull=False
    ).values_list('amount', flat=True)
    if incomes_amount:
        for amount in incomes_amount:
            total_income += amount
    return total_income


def get_total_money_USD(declaration):
    money_data = Money.objects.filter(
        declaration=declaration.id,
        amount__isnull=False,
        currency__isnull=False
    ).values_list('currency', 'amount')
    if money_data:
        return get_total_USD(money_data, declaration.year)
    return 0


def get_total_liabilities_USD(declaration):
    liabilities_data = Liability.objects.filter(
        declaration=declaration.id,
        amount__isnull=False,
        currency__isnull=False
    ).values_list('currency', 'amount')
    if liabilities_data:
        return get_total_USD(liabilities_data, declaration.year)
    return 0


def get_total_property_valuation(declaration_id):
    total_property_valuation = 0
    distinct_property_data = PropertyRight.objects.filter(
        property__declaration_id=declaration_id,
        type__in=OWNERSHIP_TYPES,
        property__valuation__isnull=False,
    ).values_list('property', 'property__valuation').distinct()
    if distinct_property_data:
        for data in distinct_property_data:
            total_property_valuation += data[1]
    return round(total_property_valuation, 2)


def get_total_cars_valuation(declaration_id):
    total_cars_valuation = 0
    distinct_cars_data = VehicleRight.objects.filter(
        car__declaration_id=declaration_id,
        car__valuation__isnull=False,
    ).values_list('car', 'car__valuation').distinct()
    if distinct_cars_data:
        for data in distinct_cars_data:
            total_cars_valuation += data[1]
    return total_cars_valuation


def get_total_hard_cash_USD(declaration):
    cash_data = Money.objects.filter(
        declaration_id=declaration.id,
        type=Money.CASH,
        amount__isnull=False
    ).values_list('currency', 'amount')
    if cash_data:
        return get_total_USD(cash_data, declaration.year)
    return 0


# from first to last
def get_pep_declarations(pep_id):
    return Declaration.objects.filter(
        pep_id=pep_id,
    ).order_by('submission_date')


def get_previous_declaration(pep_id, year):
    return Declaration.objects.filter(
        pep_id=pep_id,
        type=Declaration.ANNUAL,
        year=year - 1
    ).order_by('-submission_date').first()


class BaseScoringRule(ABC):
    rule_id = None
    message_uk = ''
    message_en = ''
    priority = 10  # priority = 1 - calculated first, priority = 2 calculated second

    class DataSerializer(serializers.Serializer):
        """ Overwrite this class in child classes """

    def __init__(self, declaration: Declaration) -> None:
        assert type(self.rule_id) == ScoringRuleEnum
        self.rule_id = self.rule_id.value
        self.declaration: Declaration = declaration
        self.pep: Pep = declaration.pep
        self.weight = None
        self.data = None

    @classmethod
    def get_message_uk(cls, data: dict) -> str:
        return cls.message_uk

    @classmethod
    def get_message_en(cls, data: dict) -> str:
        return cls.message_en

    def get_error_message(self, message: str) -> str:
        return f'{self.__class__.__name__}[{self.rule_id}][{self.declaration.nacp_declaration_id}]: {message}'

    def validate_data(self, data) -> None:
        try:
            self.DataSerializer(data=data).is_valid(raise_exception=True)
        except ValidationError as e:
            raise ValueError(self.get_error_message(f'{e} \n data = {data}'))
        try:
            self.get_message_uk(data).format(**data)
            self.get_message_en(data).format(**data)
        except KeyError:
            raise ValueError(self.get_error_message(f'`data` dont have keys for render messages'))

    def validate_weight(self, weight) -> None:
        assert type(weight) in (int, float)

    def calculate_with_validation(self) -> Tuple[Union[int, float], dict]:
        weight, data = self.calculate_weight()
        if weight != 0:
            self.validate_data(data)
            self.validate_weight(weight)
        self.weight = weight
        self.data = data
        return weight, data

    def save_to_db(self):
        assert self.weight is not None and self.data is not None
        PepScoring.objects.update_or_create(
            declaration=self.declaration,
            pep=self.pep,
            rule_id=self.rule_id,
            defaults={
                'data': self.data,
                'score': self.weight,
                'calculation_datetime': timezone.now(),
            }
        )

    @abstractmethod
    def calculate_weight(self) -> Tuple[Union[int, float], dict]:
        pass


@register_rule
class IsSpouseDeclared(BaseScoringRule):
    """
    Rule 1 - PEP01
    weight - 0.1, 0.3, 0.5, 0.7
    Asset declaration does not indicate PEP’s spouse, while pep.org.ua register has information on them
    """

    rule_id = ScoringRuleEnum.PEP01
    message_uk = (
        'У декларації про майно немає даних про члена родини, '
        'тоді як у реєстрі pep.org.ua є {relationship_type} {spouse_full_name} '
        '{spouse_companies_info}. '
    )
    message_en = 'Asset declaration does not indicate PEP\'s spouse'

    class DataSerializer(serializers.Serializer):
        relationship_type = serializers.CharField(required=True)
        spouse_full_name = serializers.CharField(required=True)
        spouse_companies_info = serializers.CharField(allow_blank=True)

    def calculate_weight(self) -> Tuple[Union[int, float], dict]:
        declarant = self.pep

        link_to_spouse_from_antac_db = RelatedPersonsLink.objects.filter(
            Q(from_person=declarant) | Q(to_person=declarant),
            to_person_relationship_type__in=SPOUSE_TYPES
        ).first()
        if link_to_spouse_from_antac_db:
            is_spouse_declared = self.declaration.spouse
            if not is_spouse_declared:
                weight = 0.1
                spouse_companies_info = ''

                spouse_from_antac_db = None
                relationship_type = None
                if link_to_spouse_from_antac_db.to_person == declarant:
                    spouse_from_antac_db = link_to_spouse_from_antac_db.from_person
                    relationship_type = link_to_spouse_from_antac_db.from_person_relationship_type
                else:
                    spouse_from_antac_db = link_to_spouse_from_antac_db.to_person
                    relationship_type = link_to_spouse_from_antac_db.to_person_relationship_type

                spouse_companies_links = CompanyLinkWithPep.objects.filter(
                    pep=spouse_from_antac_db,
                    category=CompanyLinkWithPep.OWNER,
                ).values_list('company__source', flat=True)
                if spouse_companies_links:
                    total_foreign_companies = 0
                    total_ukrainian_companies = 0
                    for source in spouse_companies_links:
                        # TODO: check if Company.ANTAC stores only foreign companies
                        if source == Company.ANTAC:
                            total_foreign_companies += 1
                        elif source == Company.UKRAINE_REGISTER:
                            total_ukrainian_companies += 1

                    if total_foreign_companies:
                        return 0.7, {
                            'relationship_type': relationship_type,
                            'spouse_full_name': spouse_from_antac_db.fullname.title(),
                            'spouse_companies_info': (
                                f'з кількістю компаній у власності, зареєстрованих за кордоном - '
                                f'{total_foreign_companies}')
                        }
                    if total_ukrainian_companies:
                        weight = 0.3
                        spouse_companies_info = (f'з кількістю компаній у власності, '
                                                 f'{total_ukrainian_companies}')
                        limit = 10
                        if total_ukrainian_companies > limit:
                            weight = 0.5

                return weight, {
                    'relationship_type': relationship_type,
                    'spouse_full_name': spouse_from_antac_db.fullname.title(),
                    'spouse_companies_info': spouse_companies_info
                }

        return RESULT_FALSE


@register_rule
class IsSmallIncome(BaseScoringRule):
    """
    Rule 2 - PEP02
    weight - 0.2, 0.5, 1
    The overall value of the property and assets exceeds income 10 or more times
    """

    rule_id = ScoringRuleEnum.PEP02
    message_uk = (
        "Задекларована вартість нерухомості та авто - {total_assets} гривень "
        "перевищує задекларовані доходи - {total_incomes} гривень у десять та більше разів"
    )
    message_en = (
        "Declared value of property and cars - {total_assets} UAH exceed "
        "declared income - {total_incomes} UAH in 10 times and more"
    )

    # we can use this later
    # message_uk = (
    #     "Задекларована вартість нерухомості, авто та грошових активів - {total_assets} гривень "
    #     "перевищує задекларовані доходи - {total_incomes} гривень у десять та більше разів"
    # )
    # message_en = (
    #     "Declared value of property, cars and monetary assets - {total_assets} UAH exceed "
    #     "declared income - {total_incomes} UAH in 10 times and more"
    # )

    class DataSerializer(serializers.Serializer):
        total_assets = serializers.FloatField(min_value=0, required=True)
        total_incomes = serializers.FloatField(min_value=0, required=True)

    def calculate_weight(self) -> Tuple[Union[int, float], dict]:
        declaration_id = self.declaration.id
        first_limit = 10
        second_limit = 50
        third_limit = 100

        total_incomes = get_total_income(self.declaration.id)
        # TODO: investigate cases with zero incomes
        if not total_incomes:
            return RESULT_FALSE

        total_property_valuation = get_total_property_valuation(declaration_id)
        total_cars_valuation = get_total_cars_valuation(declaration_id)
        total_assets = total_property_valuation + total_cars_valuation
        if not total_assets:
            return RESULT_FALSE
        result = total_assets / total_incomes
        if result > first_limit:
            weight = 0.2
            if result > second_limit:
                weight = 0.5
                if result > third_limit:
                    weight = 1
            return weight, {
                "total_assets": total_assets,
                "total_incomes": total_incomes
            }
        return RESULT_FALSE


@register_rule
class IsNoRealEstateValue(BaseScoringRule):
    """
    Rule 3.1 - PEP03_home
    weight - 0.4
    There is no information on the value of the real estate owned by PEP or
    family members since 2015
    """

    rule_id = ScoringRuleEnum.PEP03_home
    message_uk = (
        "Не зазначена вартість {total_real_estate} нерухомості, якою декларант або його родина володіє "
        "з 2015 року та пізніше"
    )
    message_en = (
        "Declared no amounting of {total_real_estate} real estate owned by PEP or family members "
        "since 2015 or later"
    )

    class DataSerializer(serializers.Serializer):
        total_real_estate = serializers.IntegerField(
            min_value=0, required=True
        )

    def calculate_weight(self) -> Tuple[Union[int, float], dict]:
        real_estate_types = [
            Property.SUMMER_HOUSE,
            Property.HOUSE,
            Property.APARTMENT,
            Property.ROOM,
            Property.UNFINISHED_CONSTRUCTION,
            Property.OFFICE
        ]

        real_estate_without_valuation = PropertyRight.objects.filter(
            property__declaration_id=self.declaration.id,
            property__valuation__isnull=True,
            property__type__in=real_estate_types,
            type__in=OWNERSHIP_TYPES,
            acquisition_date__year__gte=FIRST_DECLARING_YEAR,
        ).values_list('property_id', flat=True).distinct()
        if real_estate_without_valuation:
            return 0.4, {
                'total_real_estate': real_estate_without_valuation.count()
            }
        return RESULT_FALSE


@register_rule
class IsNoAutoValue(BaseScoringRule):
    """
    Rule 3.3 - PEP03_car
    weight - 0.1
    There is no information on the value of the declared car owned or used by PEP or
    family members since 2015
    """

    rule_id = ScoringRuleEnum.PEP03_car
    message_uk = (
        "Не зазначена вартість {total_cars} авто, якими декларант або його родина володіє "
        "чи користується з 2015 року чи пізніше"
    )
    message_en = (
        "Declared no amounting of {total_cars} cars owned or used by PEP or family members "
        "since 2015 or later"
    )

    class DataSerializer(serializers.Serializer):
        total_cars = serializers.IntegerField(
            min_value=0, required=True
        )

    def calculate_weight(self) -> Tuple[Union[int, float], dict]:
        cars_without_valuation = VehicleRight.objects.filter(
            car__declaration_id=self.declaration.id,
            car__valuation__isnull=True,
            acquisition_date__year__gte=FIRST_DECLARING_YEAR,
        ).values_list('car_id', flat=True).distinct()
        if cars_without_valuation:
            return 0.1, {
                'total_cars': cars_without_valuation.count()
            }
        return RESULT_FALSE


@register_rule
class IsResidenceHidden(BaseScoringRule):
    """
    Rule 4 - PEP04
    weight - 0.7
    There is no information on the real estate in the region where PEP declares place of residence
    """

    rule_id = ScoringRuleEnum.PEP04_reg
    message_uk = (
        "Не зазначена нерухомість в регіоні, де публічний діяч задекларував місце проживання - "
        "{residence_region}"
    )
    message_en = (
        "Declared no real-estate in the region, where place of residence we declared"
    )

    class DataSerializer(serializers.Serializer):
        residence_region = serializers.CharField(required=True)

    def calculate_weight(self) -> Tuple[Union[int, float], dict]:
        living_types = [
            Property.SUMMER_HOUSE,
            Property.HOUSE,
            Property.APARTMENT,
            Property.ROOM,
            Property.UNFINISHED_CONSTRUCTION,
            Property.OTHER
        ]
        city_of_residence = self.declaration.city_of_residence

        if not city_of_residence:
            return RESULT_FALSE
        residence_region = str(city_of_residence.region)
        result_true = 0.7, {'residence_region': residence_region.capitalize()}
        property_regions = Property.objects.filter(
            declaration=self.declaration.id,
            type__in=living_types,
            city__isnull=False,
        ).values_list('city__region__name', flat=True)[::1]
        if not property_regions:
            return result_true
        is_found = False
        for region_name in property_regions:
            # check if 'київ' in 'київ' and 'київська'
            if residence_region in region_name:
                is_found = True
        if is_found:
            return RESULT_FALSE
        else:
            return result_true


@register_rule
class IsAssetsJumped(BaseScoringRule):
    """
    Rule 05 - PEP05
    weight - 0.5
    PEP declared that the overall value of the movable and immovable property
    and hard cash increased 5 times compared to the declaration for the previous year
    """

    rule_id = ScoringRuleEnum.PEP05
    message_uk = (
        "Сума задекларованих нерухомості, авто та готівки - разом еквівалент {total_assets_USD} USD "
        "зросла більш ніж у п'ять разів порівнено з попереднім роком - {previous_total_assets_USD} USD, "
        "у той час як зобов'язання змінилися з {total_liabilities_USD} USD до "
        "{previous_total_liabilities_USD} USD"
    )
    message_en = (
        "Amounting of declared property, cars and hard cash - {total_assets_USD} USD "
        "increased more than five times from previous year - {previous_total_assets_USD} USD, "
        "and in the same time liabilities changed from {total_liabilities_USD} USD to "
        "{previous_total_liabilities_USD} USD"
    )

    class DataSerializer(serializers.Serializer):
        total_assets_USD = serializers.DecimalField(
            max_digits=12, decimal_places=2, min_value=0, required=True
        )
        previous_total_assets_USD = serializers.DecimalField(
            max_digits=12, decimal_places=2, min_value=0, required=True
        )
        total_liabilities_USD = serializers.DecimalField(
            max_digits=12, decimal_places=2, min_value=0, required=True
        )
        previous_total_liabilities_USD = serializers.DecimalField(
            max_digits=12, decimal_places=2, min_value=0, required=True
        )

    def calculate_weight(self) -> Tuple[Union[int, float], dict]:
        pep_id = self.pep.id
        year = self.declaration.year
        times_limit = 5
        difference_limit = 30000

        def get_total_assets_USD(declaration):
            total_cash_USD = get_total_hard_cash_USD(declaration)
            total_property_valuation = get_total_property_valuation(declaration.id)
            total_cars_valuation = get_total_cars_valuation(declaration.id)
            total_property_cars_USD = convert_to_usd(
                UAH,
                float(total_property_valuation + total_cars_valuation),
                declaration.year
            )
            return total_cash_USD + total_property_cars_USD

        previous_declaration = get_previous_declaration(pep_id, year)
        if not previous_declaration:
            return RESULT_FALSE
        declaration = self.declaration
        # Marriage can bring new assets, not only happiness)
        # TODO: store Declaration.spouse that is not already in the PEP DB
        if not previous_declaration.spouse and declaration.spouse:
            return RESULT_FALSE

        previous_total_assets_USD = get_total_assets_USD(previous_declaration)
        total_assets_USD = get_total_assets_USD(declaration)

        if total_assets_USD - previous_total_assets_USD < difference_limit:
            return RESULT_FALSE

        if total_assets_USD > previous_total_assets_USD * times_limit:
            return 0.5, {
                "total_assets_USD":
                    round(total_assets_USD, 2),
                "previous_total_assets_USD":
                    round(previous_total_assets_USD, 2),
                'total_liabilities_USD':
                    round(get_total_liabilities_USD(declaration), 2),
                'previous_total_liabilities_USD':
                    round(get_total_liabilities_USD(previous_declaration), 2)
            }
        return RESULT_FALSE


@register_rule
class IsAssetsSaleTrick(BaseScoringRule):
    """
    Rule 9 - PEP09
    weight - 0.5
    Income from the sale of  assets or property or cars times exceeds in 3 or more times
    the declared value of those sold assets in the declaration for the previous year
    """

    rule_id = ScoringRuleEnum.PEP09
    message_uk = (
        "Задекларовані доходи від продажу нерухомості - {total_sales_incomes} гривень "
        "більш ніж утричі перевищують задекларовану роком раніше оцінку цих активів - "
        "{previous_valuation} гривень"
    )
    message_en = (
        "Declared income from sale of property - {total_sales_incomes} UAH exceed "
        "more than three times the valuation of these property that was declared in the previous year"
        " - {previous_valuation} UAH"
    )

    # for next iteration
    # message_uk = (
    #     "Задекларовані доходи від продажу нерухомості та/або авто - {total_sales_incomes} гривень "
    #     "більш ніж утричі перевищують задекларовану роком раніше оцінку цих активів - "
    #     "{previous_valuation} гривень"
    # )
    # message_en = (
    #     "Declared income from sale of property and/or cars - {total_sales_incomes} UAH exceed "
    #     "more than three times the valuation of these assets that was declared in the previous year"
    #     " - {previous_valuation} UAH"
    # )

    class DataSerializer(serializers.Serializer):
        total_sales_incomes = serializers.DecimalField(
            max_digits=12, decimal_places=2,
            min_value=0, required=True
        )
        previous_valuation = serializers.DecimalField(
            max_digits=12, decimal_places=2,
            min_value=0, required=True
        )

    def calculate_weight(self) -> Tuple[Union[int, float], dict]:
        # ANTAC wants to add sales of cars
        sales_type = [Income.SALE_OF_PROPERTY, ]  # later we should add here Income.SALE_OF_MOVABLES
        declaration_id = self.declaration.id
        pep_id = self.pep.id
        year = self.declaration.year
        times_limit = 3

        total_sales_incomes = Income.objects.filter(
            declaration=declaration_id,
            type__in=sales_type,
            amount__isnull=False
        ).aggregate(Sum('amount')).get('amount__sum')
        if not total_sales_incomes:
            return RESULT_FALSE

        previous_declaration = get_previous_declaration(pep_id, year)
        if not previous_declaration:
            return RESULT_FALSE
        previous_property_data = PropertyRight.objects.filter(
            property__declaration=previous_declaration,
            type__in=OWNERSHIP_TYPES,
            property__valuation__isnull=False
        ).values_list('property__area', 'property__valuation', 'property').distinct()
        if not previous_property_data:
            return RESULT_FALSE
        # getting last declaration`s property area data to find sold property
        property_area_now = PropertyRight.objects.filter(
            property__declaration=declaration_id,
            type__in=OWNERSHIP_TYPES
        ).values_list('property__area', flat=True).distinct()
        previous_valuation = 0
        sold_property_id = []
        for data in previous_property_data:
            if data[0] not in property_area_now:
                previous_valuation += data[1]
                # TODO: discuss logging that data for ANTAC
                sold_property_id.append(data[2])
        if not previous_valuation:
            # TODO: discuss logging for ANTAC in such case
            return RESULT_FALSE
        if total_sales_incomes > previous_valuation * times_limit:
            return 0.5, {
                "total_sales_incomes": total_sales_incomes,
                "previous_valuation": previous_valuation
            }
        return RESULT_FALSE


@register_rule
class IsMuchPartTimeJob(BaseScoringRule):
    """
    Rule 10 - PEP10
    weight - 0.2
    Income from the part-time job exceeds 30% of the total income
    """

    rule_id = ScoringRuleEnum.PEP10
    message_uk = (
        "Задекларовані доходи декларанта від роботи  за сумісництвом - {part_time_job_incomes} гривень "
        "складають більше 30% від усіх доходів - {pep_incomes} гривень"
    )
    message_en = (
        "Declared PEP`s income from part-time job - UAH {part_time_job_incomes} exceeds "
        "more than 30% of total income - UAH {pep_incomes}"
    )

    class DataSerializer(serializers.Serializer):
        part_time_job_incomes = serializers.DecimalField(
            max_digits=12, decimal_places=2,
            min_value=0, required=True
        )
        pep_incomes = serializers.DecimalField(
            max_digits=12, decimal_places=2,
            min_value=0, required=True
        )

    def calculate_weight(self) -> Tuple[Union[int, float], dict]:
        share_limit = Decimal('.3')
        declaration_id = self.declaration.id
        pep_id = self.pep.id

        part_time_job_incomes = Income.objects.filter(
            declaration=declaration_id,
            recipient=pep_id,
            type=Income.PART_TIME_SALARY,
            amount__isnull=False
        ).aggregate(Sum('amount')).get('amount__sum')
        if not part_time_job_incomes:
            return RESULT_FALSE
        pep_incomes = Income.objects.filter(
            declaration=declaration_id,
            recipient=pep_id,
            amount__isnull=False
        ).aggregate(Sum('amount')).get('amount__sum')
        if part_time_job_incomes > pep_incomes * share_limit:
            return 0.2, {
                'part_time_job_incomes': part_time_job_incomes,
                'pep_incomes': pep_incomes
            }
        return RESULT_FALSE


@register_rule
class IsBigRoyalty(BaseScoringRule):
    """
    Rule 11 - PEP11
    weight - 0.2
    Royalty exceeds 20% of the total income
    """

    rule_id = ScoringRuleEnum.PEP11
    message_uk = 'Роялті - {total_royalty} складають більше 20% задекларованих доходів {total_income}'
    message_en = 'Royalty - {total_royalty} exceeds 20% of the total income {total_income}'

    class DataSerializer(serializers.Serializer):
        total_royalty = serializers.DecimalField(
            max_digits=12, decimal_places=2,
            min_value=0, required=True,
        )
        total_income = serializers.DecimalField(
            max_digits=12, decimal_places=2,
            min_value=0, required=True,
        )

    def calculate_weight(self) -> Tuple[Union[int, float], dict]:
        limit_times = 5

        total_royalty = 0
        total_income = 0
        incomes = Income.objects.filter(
            declaration_id=self.declaration.id,
            amount__isnull=False,
        ).values_list('amount', 'type')[::1]
        if incomes:
            for income in incomes:
                total_income += income[0]
                if income[1] == Income.ROYALTY:
                    total_royalty += income[0]
            if total_royalty * limit_times > total_income:
                return 0.2, {
                    'total_royalty': total_royalty,
                    'total_income': total_income,
                }
        return RESULT_FALSE


@register_rule
class IsMuchSpending(BaseScoringRule):
    """
    Rule 13 - PEP13
    weight - 0.7
    The overall amount of income and monetary assets indicated in the declaration
    is smaller or equal to the expenditures indicated in the declaration
    """

    rule_id = ScoringRuleEnum.PEP13
    message_uk = (
        "Задекларовані витрати - еквівалент {total_expenditures_USD} USD перевищують суму "
        "задекларованих доходів та грошових активів на кінець попереднього року - "
        "еквівалент {declared_money_USD} USD"
    )
    message_en = (
        "Declared expenditures - USD {total_expenditures_USD} exceed the sum of income "
        "and amount of monetary assets of the previous year - USD {declared_money_USD}"
    )

    class DataSerializer(serializers.Serializer):
        total_expenditures_USD = serializers.DecimalField(
            max_digits=12, decimal_places=2, min_value=0, required=True
        )
        declared_money_USD = serializers.DecimalField(
            max_digits=12, decimal_places=2, min_value=0, required=True
        )

    def calculate_weight(self) -> Tuple[Union[int, float], dict]:
        year = self.declaration.year
        declaration_id = self.declaration.id

        previous_declaration = get_previous_declaration(self.pep.id, year)
        if not previous_declaration:
            return RESULT_FALSE
        total_expenditures = Transaction.objects.filter(
            declaration=declaration_id,
            is_money_spent=True,
            amount__isnull=False
        ).aggregate(Sum('amount')).get('amount__sum')
        if not total_expenditures:
            return RESULT_FALSE
        total_expenditures_USD = convert_to_usd(UAH, float(total_expenditures), year)

        previous_total_money_USD = get_total_money_USD(previous_declaration)
        total_income_USD = convert_to_usd(UAH, float(get_total_income(declaration_id)), year)
        declared_money_USD = total_income_USD + previous_total_money_USD
        if total_expenditures_USD > declared_money_USD:
            return 0.7, {
                "total_expenditures_USD": round(total_expenditures_USD, 2),
                "declared_money_USD": round(declared_money_USD, 2)
            }
        return RESULT_FALSE


@register_rule
class IsGiftExpensive(BaseScoringRule):
    """
    Rule 15 - PEP15
    weight - 0.8, 1
    Declared gifts amounting to more than 300 000 UAH
    """
    rule_id = ScoringRuleEnum.PEP15
    message_uk = (
        "Загальна вартість задекларованих порадунків перевищує 300 тисяч гривень - {total_valuation}"
    )
    message_en = 'Total valuation of declared gifts exceeds UAH 300 000 - {total_valuation}'

    class DataSerializer(serializers.Serializer):
        total_valuation = serializers.DecimalField(
            max_digits=12, decimal_places=2, min_value=0, required=True
        )

    def calculate_weight(self) -> Tuple[Union[int, float], dict]:
        first_limit = 300000
        second_limit = 1000000
        total_valuation = 0

        gifts_valuation = Income.objects.filter(
            declaration_id=self.declaration.id,
            type__in=GIFT_TYPES,
            amount__isnull=False,
        ).values_list('amount', flat=True)
        for valuation in gifts_valuation:
            total_valuation += valuation
        if total_valuation > first_limit:
            weight = 0.8
            data = {'total_valuation': total_valuation}
            if total_valuation > second_limit:
                weight = 1
            return weight, data
        return RESULT_FALSE


@register_rule
class IsBigPrize(BaseScoringRule):
    """
    Rule 16 - PEP16
    weight - 1.0
    Declared lottery winning or prizes with a price of more than 300 000 UAH
    """

    rule_id = ScoringRuleEnum.PEP16
    message_uk = (
        "Задекларовано {total_prizes} виграші в лотерею або призи вартістю більше 300000 гривень - "
        "{total_prizes_amount}"
    )
    message_en = (
        "Declared amounting of {total_prizes} lottery wins or prizes exceed UAH 300000 - "
        "{total_prizes_amount}"
    )

    class DataSerializer(serializers.Serializer):
        total_prizes = serializers.IntegerField(
            min_value=0, required=True
        )
        total_prizes_amount = serializers.DecimalField(
            max_digits=12, decimal_places=2, min_value=0, required=True
        )

    def calculate_weight(self) -> Tuple[Union[int, float], dict]:
        limit = 300000
        prizes_amount = Income.objects.filter(
            declaration_id=self.declaration.id,
            amount__isnull=False,
            type=Income.PRIZE,
        ).values_list('amount', flat=True)
        if prizes_amount:
            total_prizes_amount = 0
            for amount in prizes_amount:
                total_prizes_amount += amount

            if total_prizes_amount > limit:
                return 1.0, {
                    'total_prizes': prizes_amount.count(),
                    'total_prizes_amount': total_prizes_amount
                }
        return RESULT_FALSE


@register_rule
class IsCarUnderestimated(BaseScoringRule):
    """
    Rule 17 - PEP17
    weight - 0.8
    Declared car produced more than 5 year ago with valuation less than 150000 UAH
    """

    rule_id = ScoringRuleEnum.PEP17
    message_uk = (
        'Задекларована вартість менше ніж 150000 гривень у {total_underestimated_cars} авто '
        'після {manufacture_year_limit} року випуску'
    )
    message_en = (
        'Declared valuation is less then UAH 150000 of {total_underestimated_cars} cars '
        'that were manufactured after {manufacture_year_limit} year'
    )

    class DataSerializer(serializers.Serializer):
        manufacture_year_limit = serializers.IntegerField(min_value=0, required=True)
        total_underestimated_cars = serializers.IntegerField(min_value=0, required=True)

    def calculate_weight(self) -> Tuple[Union[int, float], dict]:
        limit_valuation = 150000
        manufacture_year_limit = self.declaration.year - 5

        total_underestimated_cars = Vehicle.objects.filter(
            declaration_id=self.declaration.id,
            type=Vehicle.CAR,
            year__gt=manufacture_year_limit,
            # null is the case for PEP03_car rule
            valuation__isnull=False,
            valuation__lt=limit_valuation,
        ).count()
        # we can add here car`s data like via values_list('brand', 'model', 'year', 'valuation').
        if total_underestimated_cars:
            return 0.8, {
                'manufacture_year_limit': manufacture_year_limit,
                'total_underestimated_cars': total_underestimated_cars
            }
        return RESULT_FALSE


@register_rule
class IsManyCars(BaseScoringRule):
    """
    Rule 19 - PEP19
    weight - 0.5
    Declared ownership and/or right of use of more than 5 cars
    """

    rule_id = ScoringRuleEnum.PEP19
    message_uk = (
        "Задекларовано більше п'яти авто - {total_cars}"
    )
    message_en = 'Declared more than five cars - {total_cars}'

    class DataSerializer(serializers.Serializer):
        total_cars = serializers.IntegerField(min_value=0, required=True)

    def calculate_weight(self) -> Tuple[Union[int, float], dict]:
        limit = 5

        total_cars = Vehicle.objects.filter(
            declaration=self.declaration.id,
            type=Vehicle.CAR
        ).count()
        if total_cars > limit:
            return 0.5, {'total_cars': total_cars}
        return RESULT_FALSE


@register_rule
class IsMuchCash(BaseScoringRule):
    """
    Rule 20 - PEP20
    weight - 0.5, 0.8, 1
    The overall amount of declared hard cash owned by PEP and members of the family exceeds USD 50000
    """

    rule_id = ScoringRuleEnum.PEP20
    message_uk = (
        "Задекларована сума грошей у готівці - еквівалент {total_cash_USD} USD перевищує USD 50000"
    )
    message_en = (
        "Declared hard cash - USD {total_cash_USD} exceeds USD 50000"
    )

    class DataSerializer(serializers.Serializer):
        total_cash_USD = serializers.DecimalField(
            max_digits=12, decimal_places=2, min_value=0, required=True
        )

    def calculate_weight(self) -> Tuple[Union[int, float], dict]:
        declaration = self.declaration
        # check if rule22 has not been applied for the first declaration
        # FROM ANTAC: 'Якщо декларація одна тобі треба шоб спочатку працювало PEP22.
        # Якщо False - тоді PEP20'
        if get_pep_declarations(self.pep.id).count() == 1:
            if PepScoring.objects.filter(
                    declaration=declaration.id,
                    rule_id=ScoringRuleEnum.PEP22.name,
                    score__gt=0
            ).first():
                return RESULT_FALSE

        first_limit_cash = 50000
        second_limit_cash = 100000
        third_limit_cash = 500000

        total_cash_USD = get_total_hard_cash_USD(declaration)

        if total_cash_USD > first_limit_cash:
            weight = 0.5
            if total_cash_USD > second_limit_cash:
                weight = 0.8
                if total_cash_USD > third_limit_cash:
                    weight = 1
            return weight, {
                "total_cash_USD": round(total_cash_USD, 2),
            }
        return RESULT_FALSE


@register_rule
class IsMoneyFromNowhere(BaseScoringRule):
    """
    Rule 21 - PEP21
    weight - 0.8
    Monetary assets declared this year exceed the sum of this year`s
    income and amount of monetary assets of the previous year
    """

    rule_id = ScoringRuleEnum.PEP21
    message_uk = (
        "Задекларовані грошові активи - еквівалент {total_money_USD} USD перевищують суму "
        "задекларованих доходів та грошових активів на кінець попереднього року - "
        "еквівалент {declared_money_USD} USD"
    )
    message_en = (
        "Monetary assets declared this year - USD {total_money_USD} exceed the sum of income "
        "and amount of monetary assets of the previous year - "
        "USD {declared_money_USD}"
    )

    class DataSerializer(serializers.Serializer):
        total_money_USD = serializers.DecimalField(
            max_digits=12, decimal_places=2, min_value=0, required=True
        )
        declared_money_USD = serializers.DecimalField(
            max_digits=12, decimal_places=2, min_value=0, required=True
        )

    def calculate_weight(self) -> Tuple[Union[int, float], dict]:
        year = self.declaration.year

        previous_declaration = get_previous_declaration(self.pep.id, year)
        if not previous_declaration:
            return RESULT_FALSE
        previous_total_money_USD = get_total_money_USD(previous_declaration)
        total_income_USD = convert_to_usd(UAH, float(get_total_income(self.declaration.id)), year)
        declared_money_USD = total_income_USD + previous_total_money_USD
        total_money_USD = get_total_money_USD(self.declaration)
        if total_money_USD > declared_money_USD:
            return 0.8, {
                "total_money_USD": round(total_money_USD, 2),
                "declared_money_USD": round(declared_money_USD, 2)
            }
        return RESULT_FALSE


@register_rule
class IsCashTrick(BaseScoringRule):
    """
    Rule 22 - PEP22
    weight - 0.5, 0.8, 1
    Hard cash declared in the very first electronic asset declaration available in
    the system exceeds in 5 or more times income declared for the corresponding year
    """

    rule_id = ScoringRuleEnum.PEP22
    # Has to be prior to PEP20
    priority = 1
    message_uk = (
        "готівкові кошти в першій електронній декларації - {cash_USD} USD, "
        "що перевищує в {times} разів декларований дохід за відповідний рік - "
        "USD {income_USD}"
    )
    message_en = (
        "cash declared in the very first electronic asset declaration available in the system "
        "is USD {cash_USD}, that in {times} times exceeds income - USD {income_USD}"
    )

    class DataSerializer(serializers.Serializer):
        cash_USD = serializers.DecimalField(
            max_digits=12, decimal_places=2,
            min_value=0, required=True
        )
        income_USD = serializers.DecimalField(
            max_digits=12, decimal_places=2,
            min_value=0, required=True
        )
        times = serializers.DecimalField(
            max_digits=12, decimal_places=1,
            min_value=0, required=True
        )
        first_declaration = serializers.UUIDField(required=True)

    def calculate_weight(self) -> Tuple[Union[int, float], dict]:
        limit_times = 5
        first_limit_cash = 50000
        second_limit_cash = 100000
        third_limit_cash = 500000

        pep_declarations = Declaration.objects.filter(
            pep_id=self.pep.id,
        ).order_by('submission_date')

        if pep_declarations:
            first_declaration = pep_declarations[0]
            cash_USD = get_total_hard_cash_USD(first_declaration)
            if cash_USD < first_limit_cash:
                return RESULT_FALSE
            income_USD = convert_to_usd(
                UAH,
                float(get_total_income(first_declaration.id)),
                first_declaration.year
            )
            if income_USD:
                times = cash_USD / income_USD
                if times > limit_times:
                    if cash_USD > first_limit_cash:
                        weight = 0.5
                        if cash_USD > second_limit_cash:
                            weight = 0.8
                            if cash_USD > third_limit_cash:
                                weight = 1
                        return weight, {
                            'cash_USD': round(cash_USD, 2),
                            'income_USD': round(income_USD, 2),
                            'times': round(times, 1),
                            'first_declaration': str(first_declaration.nacp_declaration_id),
                        }
        return RESULT_FALSE


@register_rule
class IsHiddenBeneficiary(BaseScoringRule):
    """
    Rule 24 - PEP24
    weight - 1
    Asset declaration does not indicate companies, whose beneficiary is the declarant
    """

    rule_id = ScoringRuleEnum.PEP24
    message_uk = (
        "У декларації не вказані {total_not_declared_companies} компаній, бенефіціаріями яких, "
        "за даними реєстру pep.org.ua, є декларант"
    )
    message_en = (
        "Asset declaration does not indicate {total_not_declared_companies} companies, "
        "whose beneficiary is, according to the pep.org.ua data, the declarant"
    )

    class DataSerializer(serializers.Serializer):
        total_not_declared_companies = serializers.IntegerField(min_value=0, required=True)

    def calculate_weight(self) -> Tuple[Union[int, float], dict]:
        pep_id = self.pep.id

        data_from_antac = CompanyLinkWithPep.objects.filter(
            pep_id=pep_id,
            relationship_type__in=ANTAC_BENEFICIARY_TYPES,
            end_date__isnull=True,
            category=CompanyLinkWithPep.OWNER
        ).values_list('company_id', 'company__source')
        if not data_from_antac:
            return RESULT_FALSE
        # TODO: test if we should add here companies declared in CorporateRights
        declared_data = Beneficiary.objects.filter(
            declaration=self.declaration.id,
        ).values_list('company_id', 'company__source')
        # TODO: discuss other parameteres for comparing
        antac_companies_id_source = set(data_from_antac)
        declared_companies_id_source = set(declared_data)
        total_not_declared_companies = antac_companies_id_source - declared_companies_id_source
        if total_not_declared_companies:
            return 1, {
                'total_not_declared_companies': len(total_not_declared_companies)
            }
        return RESULT_FALSE


@register_rule
class IsCryptocurrency(BaseScoringRule):
    """
    Rule 26 - PEP26
    weight - 0.5, 0.8, 1
    Declared cryptocurrency
    """

    rule_id = ScoringRuleEnum.PEP26
    # TODO: define how to change messages here and in the PEP01
    message_uk = "Задекларовано криптовалюту {no_cryptocurrency_amount}"
    message_en = "Declared cryptocurrency"

    class DataSerializer(serializers.Serializer):
        # parameter for upgrading this rule later
        # total_cryptocurrency_USD = serializers.DecimalField(
        #     max_digits=12, decimal_places=2,
        #     min_value=0, required=True
        # )
        no_cryptocurrency_amount = serializers.CharField(allow_blank=True)

    def calculate_weight(self) -> Tuple[Union[int, float], dict]:
        cryptocurrency = IntangibleAsset.objects.filter(
            declaration_id=self.declaration.id,
            type=IntangibleAsset.CRYPTOCURRENCY
        ).values_list('valuation', flat=True)
        # ).values_list('quantity', 'cryptocurrency_type')
        if cryptocurrency:
            weight = 0.5
            # for quantity, cryptocurrency_type in cryptocurrency:
            #     if quantity is None or cryptocurrency_type is None:
            for valuation in cryptocurrency:
                if not valuation:
                    return 1.0, {
                        # 'no_cryptocurrency_amount': 'без вказання інформації про кількість або назву'
                        'no_cryptocurrency_amount': 'без вказання інформації про вартість'
                    }
            return weight, {
                'no_cryptocurrency_amount': ''
            }
        return RESULT_FALSE
        # TODO: convert cryptocurrency with quantity to USD and assess the total result


@register_rule
class IsRentManyRealEstate(BaseScoringRule):
    """
    Rule 27 - PEP27
    weight - 0.3
    PEP declared rent of real estate exceeding 300 sq. m.
    """

    rule_id = ScoringRuleEnum.PEP27
    message_uk = ('кількість об’єктів орендованої жилої нерухомості, що перевищують '
                  'площу 300 м. кв. {bigger_area_counter}')
    message_en = 'amount of rented real estate exceeding 300 sq.m. {bigger_area_counter}'

    class DataSerializer(serializers.Serializer):
        bigger_area_counter = serializers.IntegerField(min_value=0, required=True)

    def calculate_weight(self) -> Tuple[Union[int, float], dict]:
        limit = 300

        counter_property_with_bigger_area = PropertyRight.objects.filter(
            property__declaration_id=self.declaration.id,
            property__type__in=REAL_ESTATE_TYPES,
            type=PropertyRight.RENT,
            property__area__gt=limit,
        ).values_list('property', 'property__area').distinct().count()
        if counter_property_with_bigger_area:
            return 0.3, {
                "bigger_area_counter": counter_property_with_bigger_area,
            }
        return RESULT_FALSE


@register_rule
class IsLuxuryCar(BaseScoringRule):
    """
    Rule 18 - PEP18
    weight - 0.4, 0.1
    Declared ownership and/or right of use of a business class car, or car with a price exceeding 800 000 UAH
    or brand vehicle, which is considered to be a luxury car
    """
    rule_id = ScoringRuleEnum.PEP18
    link_to_list = 'https://www.me.gov.ua/vehicles/CalculatePrice'
    message_en = 'The declaration states {amount_luxury_cars} cars, the price of which is more than 800 thousand ' \
                 'hryvnias or is included in the list of cars subject to transport tax and approved by ' \
                 f'the Ministry of Economy {link_to_list}?lang=en-GB'
    message_uk = 'У декларації зазначено {amount_luxury_cars} автомобілів, ціна яких більше 800 тисяч гривень ' \
                 'або входять в перелік автомобілів, які підлягають оподаткуванню транспортним податком ' \
                 f'і затверджений Міністерством економіки {link_to_list}?lang=uk-UA'

    class DataSerializer(serializers.Serializer):
        amount_luxury_cars = serializers.IntegerField(min_value=0, required=True)

    def calculate_weight(self) -> Tuple[Union[int, float], dict]:
        amount_luxury_cars = Vehicle.objects.filter(
            declaration=self.declaration.id,
            is_luxury=True,
        ).all().count()
        if amount_luxury_cars:
            weight = 0.4 + (amount_luxury_cars - 1) * 0.1
            return weight, {
                'amount_luxury_cars': amount_luxury_cars
            }
        return RESULT_FALSE
