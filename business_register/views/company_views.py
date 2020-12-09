from django.apps import apps
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from business_register.filters import CompanyFilterSet
from business_register.models.company_models import Company
from business_register.permissions import PepSchemaToken
from business_register.serializers.company_and_pep_serializers import (
    CompanyListSerializer, CompanyDetailSerializer, HistoricalCompanySerializer, HistoricalAssigneeSerializer,
    HistoricalCompanyDetailSerializer, HistoricalFounderSerializer, HistoricalSignerSerializer
)
from data_ocean.views import CachedViewMixin, RegisterViewMixin

HistoricalCompany = apps.get_model('business_register', 'HistoricalCompany')
HistoricalAssignee = apps.get_model('business_register', 'HistoricalAssignee')
HistoricalCompanyDetail = apps.get_model('business_register', 'HistoricalCompanyDetail')
HistoricalFounder = apps.get_model('business_register', 'HistoricalFounder')
HistoricalSigner = apps.get_model('business_register', 'HistoricalSigner')


class CompanyViewSet(RegisterViewMixin,
                     CachedViewMixin,
                     viewsets.ReadOnlyModelViewSet):
    permission_classes = [RegisterViewMixin.permission_classes[0] | PepSchemaToken]
    queryset = Company.objects.select_related(
        'parent', 'company_type', 'status', 'authority', 'bylaw', 'country',
    ).prefetch_related(
        'founders', 'predecessors', 'assignees', 'signers', 'kveds', 'termination_started',
        'bancruptcy_readjustment', 'company_detail', 'exchange_data', 'relationships_with_peps',
    )
    serializer_class = CompanyListSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_class = CompanyFilterSet
    search_fields = ('name', 'edrpou', 'address', 'status__name')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CompanyDetailSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        if self.action == 'list':
            return self.queryset.exclude(from_antac_only=True).filter(country__name='ukraine')
        return self.queryset.filter(country__name='ukraine')


class HistoricalAssigneeView(RegisterViewMixin,
                             CachedViewMixin,
                             viewsets.ReadOnlyModelViewSet):
    queryset = HistoricalAssignee.objects.all()
    serializer_class = HistoricalAssigneeSerializer


class HistoricalCompanyView(RegisterViewMixin,
                            CachedViewMixin,
                            viewsets.ReadOnlyModelViewSet):
    queryset = HistoricalCompany.objects.all()
    serializer_class = HistoricalCompanySerializer


class HistoricalCompanyDetailView(RegisterViewMixin,
                                  CachedViewMixin,
                                  viewsets.ReadOnlyModelViewSet):
    queryset = HistoricalCompanyDetail.objects.all()
    serializer_class = HistoricalCompanyDetailSerializer


class HistoricalFounderView(RegisterViewMixin,
                            CachedViewMixin,
                            viewsets.ReadOnlyModelViewSet):
    queryset = HistoricalFounder.objects.all()
    serializer_class = HistoricalFounderSerializer


class HistoricalSignerView(RegisterViewMixin,
                           CachedViewMixin,
                           viewsets.ReadOnlyModelViewSet):
    queryset = HistoricalSigner.objects.all()
    serializer_class = HistoricalSignerSerializer
