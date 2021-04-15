from django_filters import rest_framework as filters

from location_register.models.drv_models import DrvBuilding
from location_register.models.koatuu_models import (KoatuuFirstLevel, KoatuuSecondLevel,
                                                    KoatuuThirdLevel, KoatuuFourthLevel)
from location_register.models.ratu_models import RatuStreet


class RatuStreetFilterSet(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')

    o = filters.OrderingFilter(
        fields=(
            ('region__name', 'region'),
            ('district__name', 'district'),
            ('city__name', 'city'),
            ('name', 'name'),
        ), help_text='Sort by fields: region, district, city, name.'
    )

    class Meta:
        model = RatuStreet
        fields = ()


class DrvBuildingFilterSet(filters.FilterSet):
    number = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = DrvBuilding
        fields = ()


class KoatuuFirstLevelFilterSet(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = KoatuuFirstLevel
        fields = ()


class KoatuuSecondLevelFilterSet(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    category = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = KoatuuSecondLevel
        fields = ()


class KoatuuThirdLevelFilterSet(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    category = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = KoatuuThirdLevel
        fields = ()


class KoatuuFourthLevelFilterSet(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')

    o = filters.OrderingFilter(
        fields=(
            ('code', 'code'),
            ('name', 'name'),
            ('first_level__name', 'first_level'),
            ('second_level__name', 'second_level'),
            ('third_level__name', 'third_level'),
        ),
        help_text='Sort by fields: code, name, first level of subordination, second level of subordination, \
            third level of subordination.'
    )

    class Meta:
        model = KoatuuFourthLevel
        fields = ()
