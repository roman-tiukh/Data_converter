from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from business_register.filters import CompanyFilterSet
from business_register.models.company_models import Company, HistoricalCompany
from business_register.serializers.company_and_pep_serializers import (CompanyListSerializer,
                                                                       CompanyDetailSerializer,
                                                                       HistoricalCompanySerializer)
from data_ocean.views import CachedViewMixin
from rest_framework.filters import SearchFilter


class CompanyViewSet(CachedViewMixin, viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    queryset = Company.objects.select_related(
        'parent', 'company_type', 'status', 'authority', 'bylaw',
    ).prefetch_related(
        'founders', 'predecessors', 'assignees', 'signers', 'kveds', 'termination_started',
        'bancruptcy_readjustment', 'company_detail', 'exchange_data', 'relationships_with_peps',
    ).exclude(from_antac_only=True)
    serializer_class = CompanyListSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_class = CompanyFilterSet
    search_fields = ('name', 'edrpou', 'address')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CompanyDetailSerializer
        return super().get_serializer_class()


class HistoricalCompanyView(CachedViewMixin, viewsets.ReadOnlyModelViewSet):
    queryset = HistoricalCompany.objects.all()
    serializer_class = HistoricalCompanySerializer
