from django.apps import apps
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response

from business_register.filters import CompanyFilterSet, HistoricalFounderFilterSet
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
        return self.queryset


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
    lookup_field = 'company_id'
    queryset = HistoricalFounder.objects.all()
    serializer_class = HistoricalFounderSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['history_date']
    ordering = ['-history_date']
    filterset_class = HistoricalFounderFilterSet

    def retrieve(self, request, company_id):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.filter(company_id=company_id)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class HistoricalSignerView(RegisterViewMixin,
                           CachedViewMixin,
                           viewsets.ReadOnlyModelViewSet):
    queryset = HistoricalSigner.objects.all()
    serializer_class = HistoricalSignerSerializer
