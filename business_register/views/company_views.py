from rest_framework import viewsets
from business_register.models.company_models import Company, HistoricalCompany
from business_register.serializers.company_serializers import CompanySerializer, HistoricalCompanySerializer
from data_ocean.views import CachedViewMixin


class CompanyView(CachedViewMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

class HistoricalCompanyView(CachedViewMixin, viewsets.ReadOnlyModelViewSet):
    queryset = HistoricalCompany.objects.all()
    serializer_class = HistoricalCompanySerializer
