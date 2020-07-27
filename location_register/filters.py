import django_filters
from .models.ratu_models import RatuStreet
from .models.drv_models import DrvBuilding


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
