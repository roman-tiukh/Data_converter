from django.apps import apps
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from business_register.filters import CompanyFilterSet, HistoricalCompanyRelatedFilterSet
from business_register.models.company_models import Company
from business_register.permissions import PepSchemaToken
from business_register.serializers.company_and_pep_serializers import (
    CompanyListSerializer, CompanyDetailSerializer, HistoricalAssigneeSerializer,
    HistoricalBancruptcyReadjustmentSerializer, HistoricalCompanySerializer, HistoricalCompanyDetailSerializer,
    HistoricalCompanyToKvedSerializer, HistoricalCompanyToPredecessorSerializer,
    HistoricalExchangeDataCompanySerializer, HistoricalFounderSerializer, HistoricalSignerSerializer,
    HistoricalTerminationStartedSerializer
)
from data_converter.pagination import CachedCountPagination
from data_ocean.views import CachedViewSetMixin, RegisterViewMixin

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


@method_decorator(name='retrieve', decorator=swagger_auto_schema(tags=['business register']))
@method_decorator(name='list', decorator=swagger_auto_schema(tags=['business register']))
class CompanyViewSet(RegisterViewMixin,
                     CachedViewSetMixin,
                     viewsets.ReadOnlyModelViewSet):
    permission_classes = [RegisterViewMixin.permission_classes[0] | PepSchemaToken]
    pagination_class = CachedCountPagination
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


@method_decorator(name='retrieve', decorator=swagger_auto_schema(tags=['business register']))
@method_decorator(name='list', decorator=swagger_auto_schema(tags=['business register']))
class CompanyUkrViewSet(RegisterViewMixin,
                        CachedViewSetMixin,
                        viewsets.ReadOnlyModelViewSet):
    permission_classes = [RegisterViewMixin.permission_classes[0] | PepSchemaToken]
    pagination_class = CachedCountPagination
    queryset = Company.objects.filter(
        source=Company.UKRAINE_REGISTER
    ).select_related(
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


@method_decorator(name='retrieve', decorator=swagger_auto_schema(tags=['business register']))
@method_decorator(name='list', decorator=swagger_auto_schema(tags=['business register']))
class CompanyUkViewSet(RegisterViewMixin,
                       CachedViewSetMixin,
                       viewsets.ReadOnlyModelViewSet):
    permission_classes = [RegisterViewMixin.permission_classes[0] | PepSchemaToken]
    pagination_class = CachedCountPagination
    queryset = Company.objects.filter(
        source=Company.GREAT_BRITAIN_REGISTER
    ).select_related(
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


class HistoricalCompanyRelatedViewSet(RegisterViewMixin,
                                      CachedViewSetMixin,
                                      viewsets.ReadOnlyModelViewSet):
    lookup_field = 'company_id'
    filter_backends = [DjangoFilterBackend]
    filterset_class = HistoricalCompanyRelatedFilterSet

    def retrieve(self, request, company_id):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.filter(company_id=company_id)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


@method_decorator(name='retrieve', decorator=swagger_auto_schema(tags=['business register'], auto_schema=None))
@method_decorator(name='list', decorator=swagger_auto_schema(tags=['business register'], auto_schema=None))
class HistoricalAssigneeView(HistoricalCompanyRelatedViewSet):
    queryset = HistoricalAssignee.objects.order_by('-history_date')
    serializer_class = HistoricalAssigneeSerializer


@method_decorator(name='retrieve', decorator=swagger_auto_schema(tags=['business register'], auto_schema=None))
@method_decorator(name='list', decorator=swagger_auto_schema(tags=['business register'], auto_schema=None))
class HistoricalBancruptcyReadjustmentView(HistoricalCompanyRelatedViewSet):
    queryset = HistoricalBancruptcyReadjustment.objects.order_by('-history_date')
    serializer_class = HistoricalBancruptcyReadjustmentSerializer


@method_decorator(name='retrieve', decorator=swagger_auto_schema(tags=['business register'], auto_schema=None))
@method_decorator(name='list', decorator=swagger_auto_schema(tags=['business register'], auto_schema=None))
class HistoricalCompanyView(HistoricalCompanyRelatedViewSet):
    queryset = HistoricalCompany.objects.order_by('-history_date')
    serializer_class = HistoricalCompanySerializer

    def retrieve(self, request, company_id):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.filter(id=company_id)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


@method_decorator(name='retrieve', decorator=swagger_auto_schema(tags=['business register'], auto_schema=None))
@method_decorator(name='list', decorator=swagger_auto_schema(tags=['business register'], auto_schema=None))
class HistoricalCompanyDetailView(HistoricalCompanyRelatedViewSet):
    queryset = HistoricalCompanyDetail.objects.order_by('-history_date')
    serializer_class = HistoricalCompanyDetailSerializer


@method_decorator(name='retrieve', decorator=swagger_auto_schema(tags=['business register'], auto_schema=None))
@method_decorator(name='list', decorator=swagger_auto_schema(tags=['business register'], auto_schema=None))
class HistoricalCompanyToKvedView(HistoricalCompanyRelatedViewSet):
    queryset = HistoricalCompanyToKved.objects.order_by('-history_date')
    serializer_class = HistoricalCompanyToKvedSerializer


@method_decorator(name='retrieve', decorator=swagger_auto_schema(tags=['business register'], auto_schema=None))
@method_decorator(name='list', decorator=swagger_auto_schema(tags=['business register'], auto_schema=None))
class HistoricalCompanyToPredecessorView(HistoricalCompanyRelatedViewSet):
    queryset = HistoricalCompanyToPredecessor.objects.order_by('-history_date')
    serializer_class = HistoricalCompanyToPredecessorSerializer


@method_decorator(name='retrieve', decorator=swagger_auto_schema(tags=['business register'], auto_schema=None))
@method_decorator(name='list', decorator=swagger_auto_schema(tags=['business register'], auto_schema=None))
class HistoricalExchangeDataCompanyView(HistoricalCompanyRelatedViewSet):
    queryset = HistoricalExchangeDataCompany.objects.order_by('-history_date')
    serializer_class = HistoricalExchangeDataCompanySerializer


@method_decorator(name='retrieve', decorator=swagger_auto_schema(tags=['business register'], auto_schema=None))
@method_decorator(name='list', decorator=swagger_auto_schema(tags=['business register'], auto_schema=None))
class HistoricalFounderView(HistoricalCompanyRelatedViewSet):
    queryset = HistoricalFounder.objects.order_by('-history_date')
    serializer_class = HistoricalFounderSerializer


@method_decorator(name='retrieve', decorator=swagger_auto_schema(tags=['business register'], auto_schema=None))
@method_decorator(name='list', decorator=swagger_auto_schema(tags=['business register'], auto_schema=None))
class HistoricalSignerView(HistoricalCompanyRelatedViewSet):
    queryset = HistoricalSigner.objects.order_by('-history_date')
    serializer_class = HistoricalSignerSerializer


@method_decorator(name='retrieve', decorator=swagger_auto_schema(tags=['business register'], auto_schema=None))
@method_decorator(name='list', decorator=swagger_auto_schema(tags=['business register'], auto_schema=None))
class HistoricalTerminationStartedView(HistoricalCompanyRelatedViewSet):
    queryset = HistoricalTerminationStarted.objects.order_by('-history_date')
    serializer_class = HistoricalTerminationStartedSerializer
