import django_filters

from location_register.models.drv_models import DrvBuilding
from location_register.models.koatuu_models import (KoatuuFirstLevel, KoatuuSecondLevel,
                                                    KoatuuThirdLevel, KoatuuFourthLevel)
from location_register.models.ratu_models import RatuStreet


class RatuStreetFilterSet(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = RatuStreet
        fields = ()


class DrvBuildingFilterSet(django_filters.FilterSet):
    number = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = DrvBuilding
        fields = ()


class KoatuuFirstLevelFilterSet(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = KoatuuFirstLevel
        fields = ()


class KoatuuSecondLevelFilterSet(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    category = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = KoatuuSecondLevel
        fields = ()


class KoatuuThirdLevelFilterSet(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    category = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = KoatuuThirdLevel
        fields = ()


class KoatuuFourthLevelFilterSet(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = KoatuuFourthLevel
        fields = ()
