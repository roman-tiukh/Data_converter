import decimal
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
    PepScoring,
)
from business_register.models.pep_models import CompanyLinkWithPep
from business_register.models.company_models import Company
from business_register.models.pep_models import (RelatedPersonsLink, Pep)
from business_register.pep_scoring.rules_registry import register_rule, ScoringRuleEnum
from location_register.models.ratu_models import RatuCity
from data_ocean.utils import convert_to_usd

SPOUSE_TYPES = ['дружина', 'чоловік']
GIFT_TYPES = [Income.GIFT_IN_CASH, Income.GIFT]
UAH = 'UAH'


def count_total_income(declaration_id):
    total_income = 0

    incomes_amount = Income.objects.filter(
        declaration=declaration_id,
        amount__isnull=False
    ).values_list('amount', flat=True)
    if incomes_amount:
        for amount in incomes_amount:
            total_income += amount
    return total_income


def get_total_in_USD(data, year):
    total_USD = 0

    if data:
        for currency, amount in data:
            total_USD += convert_to_usd(currency, float(amount), year)
    return total_USD


class BaseScoringRule(ABC):
    rule_id = None
    message_uk = ''
    message_en = ''

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
    weight - 0.1, 0.7
    Asset declaration does not indicate PEP’s spouse, while pep.org.ua register has information on them
    """

    rule_id = ScoringRuleEnum.PEP01
    message_uk = (
        'У декларації про майно немає даних про члена родини, '
        'тоді як у реєстрі pep.org.ua є {relationship_type} {spouse_full_name} '
        '{spouse_foreign_companies_info}. '
    )
    message_en = 'Asset declaration does not indicate PEP\'s spouse'

    class DataSerializer(serializers.Serializer):
        relationship_type = serializers.CharField(required=True)
        spouse_full_name = serializers.CharField(required=True)
        spouse_foreign_companies_info = serializers.CharField(allow_blank=True)

    def calculate_weight(self) -> Tuple[Union[int, float], dict]:
        link_to_spouse_from_antac_db = RelatedPersonsLink.objects.filter(
            from_person=self.pep,
            to_person_relationship_type__in=SPOUSE_TYPES
        ).first()
        if link_to_spouse_from_antac_db:
            is_spouse_declared = self.declaration.spouse
            if not is_spouse_declared:
                spouse_from_antac_db = link_to_spouse_from_antac_db.to_person

                spouse_foreign_companies_links = CompanyLinkWithPep.objects.filter(
                    pep=spouse_from_antac_db,
                    category=CompanyLinkWithPep.OWNER,
                    # looking for only foreign companies
                    # TODO: check if Company.ANTAC stores only foreign companies
                    company__source=Company.ANTAC
                )
                if spouse_foreign_companies_links:
                    weight = 0.7
                    spouse_foreign_companies_info = (f'з кількістю компаній, зареєстрованих за кордоном - '
                                                     f'{spouse_foreign_companies_links.count()}')
                else:
                    weight = 0.1
                    spouse_foreign_companies_info = ''

                return weight, {
                    'relationship_type': link_to_spouse_from_antac_db.to_person_relationship_type,
                    'spouse_full_name': spouse_from_antac_db.fullname.title(),
                    'spouse_foreign_companies_info': spouse_foreign_companies_info
                }

        return 0, {}


# @register_rule
class IsRealEstateWithoutValue(BaseScoringRule):
    """
    Rule 3.1 - PEP03_home
    weight - 0.4
    There is no information on the value of the real estate owned by PEP or
    family members since 2015
    """

    rule_id = ScoringRuleEnum.PEP03_home

    class DataSerializer(serializers.Serializer):
        property_id = serializers.IntegerField(min_value=0, required=True)
        declaration_id = serializers.IntegerField(min_value=0, required=True)

    def calculate_weight(self) -> Tuple[Union[int, float], dict]:
        family_ids = self.pep.related_persons.filter(
            to_person_links__category=RelatedPersonsLink.FAMILY,
        ).values_list('id', flat=True)[::1]
        family_ids.append(self.pep.id)
        have_weight = PropertyRight.objects.filter(
            pep_id__in=family_ids,
            property__valuation__isnull=True,
            type=Property.SUMMER_HOUSE,
            acquisition_date__year__gte=2015,
        ).values_list('property_id', 'property__declaration_id')[::1]
        if have_weight:
            weight = 0.4
            data = {
                "property_id": have_weight[0][0],
                "declaration_id": have_weight[0][1],
            }
            return weight, data
        return 0, {}


# @register_rule
class IsLandWithoutValue(BaseScoringRule):
    """
    Rule 3.2 - PEP03_land
    weight - 0.1
    There is no information on the value of the land owned by PEP or
    family members since 2015
    """

    rule_id = ScoringRuleEnum.PEP03_land

    class DataSerializer(serializers.Serializer):
        property_id = serializers.IntegerField(min_value=0, required=True)
        declaration_id = serializers.IntegerField(min_value=0, required=True)

    def calculate_weight(self) -> Tuple[Union[int, float], dict]:
        family_ids = self.pep.related_persons.filter(
            to_person_links__category=RelatedPersonsLink.FAMILY,
        ).values_list('id', flat=True)[::1]
        family_ids.append(self.pep.id)
        have_weight = PropertyRight.objects.filter(
            pep_id__in=family_ids,
            property__valuation__isnull=True,
            type=Property.LAND,
            acquisition_date__year__gte=2015,
        ).values_list('property_id', 'property__declaration_id')[::1]
        if have_weight:
            weight = 0.1
            data = {
                "property_id": have_weight[0][0],
                "declaration_id": have_weight[0][1],
            }
            return weight, data
        return 0, {}


# @register_rule
class IsAutoWithoutValue(BaseScoringRule):
    """
    Rule 3.3 - PEP03_car
    weight - 0.4
    There is no information on the value of the vehicle owned by PEP or
    family members since 2015
    """

    rule_id = ScoringRuleEnum.PEP03_car

    class DataSerializer(serializers.Serializer):
        vehicle_id = serializers.IntegerField(min_value=0, required=True)
        declaration_id = serializers.IntegerField(min_value=0, required=True)

    def calculate_weight(self) -> Tuple[Union[int, float], dict]:
        family_ids = self.pep.related_persons.filter(
            to_person_links__category=RelatedPersonsLink.FAMILY,
        ).values_list('id', flat=True)[::1]
        family_ids.append(self.pep.id)
        have_weight = VehicleRight.objects.filter(
            pep_id__in=family_ids,
            car__valuation__isnull=True,
            acquisition_date__year__gte=2015,
        ).values_list('car_id', 'car__declaration_id')[::1]
        if have_weight:
            weight = 0.4
            data = {
                "vehicle_id": have_weight[0][0],
                "declaration_id": have_weight[0][1],
            }
            return weight, data
        return 0, {}


@register_rule
class IsRoyaltyPart(BaseScoringRule):
    """
    Rule 11 - PEP11
    weight - 0.2
    Royalty exceeds 20% of the total income indicated in the declaration
    """

    rule_id = ScoringRuleEnum.PEP11
    message_uk = 'Роялті {royalty_UAH} перевищує 20% від загального доходу {assets_UAH}, зазначеного в декларації'
    message_en = 'Royalty {royalty_UAH} exceeds 20% of the total income {assets_UAH} indicated in the declaration'

    class DataSerializer(serializers.Serializer):
        royalty_UAH = serializers.DecimalField(
            max_digits=12, decimal_places=2,
            min_value=0, required=True,
        )
        assets_UAH = serializers.DecimalField(
            max_digits=12, decimal_places=2,
            min_value=0, required=True,
        )

    def calculate_weight(self) -> Tuple[Union[int, float], dict]:
        assets_UAH = 0
        royalty_UAH = 0
        incomes = Income.objects.filter(
            declaration_id=self.declaration.id,
            amount__isnull=False,
        ).values_list('amount', 'type')[::1]
        for income in incomes:
            assets_UAH += income[0]
            if income[1] == Income.DIVIDENDS:
                royalty_UAH += income[0]
        if royalty_UAH * 5 > assets_UAH:
            weight = 0.2
            data = {
                "royalty_UAH": royalty_UAH,
                "assets_UAH": assets_UAH,
            }
            return weight, data
        return 0, {}


@register_rule
class IsGiftExpensive(BaseScoringRule):
    """
    Rule 15 - PEP15
    weight - 0.8, 1
    Declared gift amounting to more than 300 000 UAH
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
        else:
            return 0, {}


@register_rule
class IsBigPrize(BaseScoringRule):
    """
    Rule 16 - PEP16
    weight - 1.0
    Declared lottery winning or prize with a price of more than 300 000 UAH
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
        else:
            return 0, {}


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
            year__gte=manufacture_year_limit,
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
        return 0, {}


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
        return 0, {}


@register_rule
class IsMoneyFromNowhere(BaseScoringRule):
    """
    Rule 21 - PEP21
    weight - 0.8
    Monetary assets declared this year exceed the sum of
    income and amount of monetary assets of the previous year
    """

    rule_id = ScoringRuleEnum.PEP21
    message_uk = (
        "Задекларовані грошові активи - еквівалент {total_money_USD} USD перевищують суму "
        "задекларованих доходів та грошових активів на кінець попереднього року - "
        "еквівалент {declared_assets_USD} USD"
    )
    message_en = (
        "Monetary assets declared this year - USD {total_money_USD} exceed the sum of income "
        "and amount of monetary assets of the previous year - "
        "USD {declared_assets_USD}"
    )

    class DataSerializer(serializers.Serializer):
        total_money_USD = serializers.DecimalField(
            max_digits=12, decimal_places=2, min_value=0, required=True
        )
        declared_assets_USD = serializers.DecimalField(
            max_digits=12, decimal_places=2, min_value=0, required=True
        )

    def calculate_weight(self) -> Tuple[Union[int, float], dict]:
        year = self.declaration.year
        previous_declaration = Declaration.objects.filter(
            pep_id=self.pep.id,
            type=Declaration.ANNUAL,
            year=year - 1
        ).first()
        if not previous_declaration:
            return 0, {}
        previous_money_data = Money.objects.filter(
            declaration=previous_declaration.id,
            amount__isnull=False,
            currency__isnull=False
        ).values_list('currency', 'amount')
        money_data = Money.objects.filter(
            declaration=self.declaration.id,
            amount__isnull=False,
            currency__isnull=False
        ).values_list('currency', 'amount')
        previous_total_money_USD = get_total_in_USD(previous_money_data, year - 1)
        total_money_USD = get_total_in_USD(money_data, year)
        total_income_USD = convert_to_usd(UAH, float(count_total_income(self.declaration.id)), year)
        declared_assets_USD = total_income_USD + previous_total_money_USD

        if total_money_USD > declared_assets_USD:
            return 0.8, {
                "total_money_USD": total_money_USD,
                "declared_assets_USD": declared_assets_USD
            }
        return 0, {}


@register_rule
class IsRentManyRE(BaseScoringRule):
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
        property_types = [Property.SUMMER_HOUSE, Property.HOUSE, Property.APARTMENT, Property.ROOM]
        bigger_area = PropertyRight.objects.filter(
            property__declaration_id=self.declaration.id,
            property__type__in=property_types,
            type=PropertyRight.RENT,
            property__area__gt=300,
        ).all().count()
        if bigger_area > 0:
            weight = 0.3
            data = {
                "bigger_area_counter": bigger_area,
            }
            return weight, data
        return 0, {}
