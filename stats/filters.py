from django_filters import rest_framework as filters
from business_register.models.company_models import Company


class RegisteredCompaniesCountFilterSet(filters.FilterSet):
    registration_date = filters.DateFromToRangeFilter()

    class Meta:
        model = Company
        fields = ()
