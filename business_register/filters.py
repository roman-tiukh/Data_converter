from django_filters import rest_framework as filters
from .models.company_models import Company
from .models.kved_models import Kved


class CompanyFilterSet(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    address = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Company
        fields = {
            'edrpou': ['exact'],
        }


class KvedFilterSet(filters.FilterSet):
    code = filters.CharFilter(lookup_expr='icontains')
    name = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Kved
        fields = ()
