from django_filters import rest_framework as filters
from business_register.models.company_models import Company
from business_register.models.fop_models import Fop


class RegisteredCompaniesCountFilterSet(filters.FilterSet):
    registration_date = filters.DateFromToRangeFilter()

    class Meta:
        model = Company
        fields = ()


class RegisteredFopsCountFilterSet(filters.FilterSet):
    registration_date = filters.DateFromToRangeFilter()

    class Meta:
        model = Fop
        fields = ()
