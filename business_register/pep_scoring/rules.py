from abc import ABC, abstractmethod

from django.utils import timezone
from rest_framework import serializers
from typing import Tuple, Union

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
from business_register.models.pep_models import (RelatedPersonsLink, Pep)
from business_register.pep_scoring.constants import ScoringRuleEnum
from location_register.models.ratu_models import RatuCity


ALL_RULES = {}


def register_rule(class_):
    ALL_RULES[class_.rule_id.value] = class_
    return class_


class BaseScoringRule(ABC):
    rule_id = None

    class DataSerializer(serializers.Serializer):
        """ Overwrite this class in child classes """

    def __init__(self, declaration: Declaration) -> None:
        assert type(self.rule_id) == ScoringRuleEnum
        self.rule_id = self.rule_id.value
        self.declaration: Declaration = declaration
        self.pep: Pep = declaration.pep
        self.weight = None
        self.data = None

    def validate_data(self, data) -> None:
        self.DataSerializer(data=data).is_valid(raise_exception=True)

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


@register_rule
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


@register_rule
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
class IsCostlyPresents(BaseScoringRule):
    """
    Rule 15 - PEP15
    weight - 0.8
    Declared presents amounting to more than 100 000 UAH
    """
    rule_id = ScoringRuleEnum.PEP15
    class DataSerializer(serializers.Serializer):
        presents_prise_UAH = serializers.IntegerField(min_value=0, required=True)

    def calculate_weight(self) -> Tuple[Union[int, float], dict]:
        presents_max_amount = 100000
        presents_price_UAH = 0
        incomes = Income.objects.filter(
            declaration_id=self.declaration.id,
        ).values_list('amount', 'type')[::1]
        for income in incomes:
            if income[1] in (Income.GIFT_IN_CASH, Income.GIFT):
                presents_price_UAH += income[0]
        if presents_price_UAH > presents_max_amount:
            weight = 0.8
            data = {
                "presents_price_UAH": presents_price_UAH,
            }
            return weight, data
        return 0, {}
