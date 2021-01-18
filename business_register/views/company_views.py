from django.apps import apps
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from business_register.filters import (
    CompanyFilterSet, HistoricalAssigneeFilterSet, HistoricalBancruptcyReadjustmentFilterSet,
    HistoricalCompanyFilterSet, HistoricalCompanyDetailFilterSet, HistoricalCompanyToKvedFilterSet,
    HistoricalCompanyToPredecessorFilterSet, HistoricalExchangeDataCompanyFilterSet,
    HistoricalFounderFilterSet, HistoricalSignerFilterSet, HistoricalTerminationStartedFilterSet
)
from business_register.models.company_models import Company
from business_register.permissions import PepSchemaToken
from business_register.serializers.company_and_pep_serializers import (
    CompanyListSerializer, CompanyDetailSerializer, HistoricalAssigneeSerializer,
    HistoricalBancruptcyReadjustmentSerializer, HistoricalCompanySerializer, HistoricalCompanyDetailSerializer,
    HistoricalCompanyToKvedSerializer, HistoricalCompanyToPredecessorSerializer,
    HistoricalExchangeDataCompanySerializer, HistoricalFounderSerializer, HistoricalSignerSerializer,
    HistoricalTerminationStartedSerializer
)
from data_ocean.views import CachedViewMixin, RegisterViewMixin

HistoricalAssignee = apps.get_model('business_register', 'HistoricalAssignee')
HistoricalBancruptcyReadjustment = apps.get_model('business_register', 'HistoricalBancruptcyReadjustment')
HistoricalCompany = apps.get_model('business_register', 'HistoricalCompany')
HistoricalCompanyDetail = apps.get_model('business_register', 'HistoricalCompanyDetail')
HistoricalCompanyToKved = apps.get_model('business_register', 'HistoricalCompanyToKved')
HistoricalCompanyToPredecessor = apps.get_model('business_register', 'HistoricalCompanyToPredecessor')
HistoricalExchangeDataCompany = apps.get_model('business_register', 'HistoricalExchangeDataCompany')
HistoricalFounder = apps.get_model('business_register', 'HistoricalFounder')
HistoricalSigner = apps.get_model('business_register', 'HistoricalSigner')
HistoricalTerminationStarted = apps.get_model('business_register', 'HistoricalTerminationStarted')


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


class HistoricalCompanyRelatedViewSet(RegisterViewMixin,
                                      CachedViewMixin,
                                      viewsets.ReadOnlyModelViewSet):
    lookup_field = 'company_id'
    filter_backends = [DjangoFilterBackend]

    def retrieve(self, request, company_id):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.filter(company_id=company_id)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class HistoricalAssigneeView(HistoricalCompanyRelatedViewSet):
    queryset = HistoricalAssignee.objects.order_by('-history_date')
    serializer_class = HistoricalAssigneeSerializer
    filterset_class = HistoricalAssigneeFilterSet


class HistoricalBancruptcyReadjustmentView(HistoricalCompanyRelatedViewSet):
    queryset = HistoricalBancruptcyReadjustment.objects.order_by('-history_date')
    serializer_class = HistoricalBancruptcyReadjustmentSerializer
    filterset_class = HistoricalBancruptcyReadjustmentFilterSet


class HistoricalCompanyView(HistoricalCompanyRelatedViewSet):
    queryset = HistoricalCompany.objects.order_by('-history_date')
    serializer_class = HistoricalCompanySerializer
    filterset_class = HistoricalCompanyFilterSet


class HistoricalCompanyDetailView(HistoricalCompanyRelatedViewSet):
    queryset = HistoricalCompanyDetail.objects.order_by('-history_date')
    serializer_class = HistoricalCompanyDetailSerializer
    filterset_class = HistoricalCompanyDetailFilterSet


class HistoricalCompanyToKvedView(HistoricalCompanyRelatedViewSet):
    queryset = HistoricalCompanyToKved.objects.order_by('-history_date')
    serializer_class = HistoricalCompanyToKvedSerializer
    filterset_class = HistoricalCompanyToKvedFilterSet


class HistoricalCompanyToPredecessorView(HistoricalCompanyRelatedViewSet):
    queryset = HistoricalCompanyToPredecessor.objects.order_by('-history_date')
    serializer_class = HistoricalCompanyToPredecessorSerializer
    filterset_class = HistoricalCompanyToPredecessorFilterSet


class HistoricalExchangeDataCompanyView(HistoricalCompanyRelatedViewSet):
    queryset = HistoricalExchangeDataCompany.objects.order_by('-history_date')
    serializer_class = HistoricalExchangeDataCompanySerializer
    filterset_class = HistoricalExchangeDataCompanyFilterSet


class HistoricalFounderView(HistoricalCompanyRelatedViewSet):
    queryset = HistoricalFounder.objects.order_by('-history_date')
    serializer_class = HistoricalFounderSerializer
    filterset_class = HistoricalFounderFilterSet


class HistoricalSignerView(HistoricalCompanyRelatedViewSet):
    queryset = HistoricalSigner.objects.order_by('-history_date')
    serializer_class = HistoricalSignerSerializer
    filterset_class = HistoricalSignerFilterSet


class HistoricalTerminationStartedView(HistoricalCompanyRelatedViewSet):
    queryset = HistoricalTerminationStarted.objects.order_by('-history_date')
    serializer_class = HistoricalTerminationStartedSerializer
    filterset_class = HistoricalTerminationStartedFilterSet
