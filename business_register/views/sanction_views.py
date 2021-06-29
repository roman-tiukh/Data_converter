from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.filters import SearchFilter

from business_register.filters import CompanySanctionFilterSet, PersonSanctionFilterSet
from business_register.models.sanction_models import PersonSanction, CompanySanction, CountrySanction
from business_register.serializers.sanction_serializers import (
    CountrySanctionSerializer, PersonSanctionSerializer, CompanySanctionSerializer
)
from data_converter.filter import DODjangoFilterBackend
from data_ocean.views import CachedViewSetMixin, RegisterViewMixin
from payment_system.permissions import FreeForPayedProjects


@method_decorator(name='retrieve', decorator=swagger_auto_schema(tags=['sanctions']))
@method_decorator(name='list', decorator=swagger_auto_schema(tags=['sanctions']))
class CountrySanctionViewSet(RegisterViewMixin,
                             CachedViewSetMixin,
                             viewsets.ReadOnlyModelViewSet):
    permission_classes = [FreeForPayedProjects]
    queryset = CountrySanction.objects.all()
    serializer_class = CountrySanctionSerializer
    filter_backends = (DODjangoFilterBackend, SearchFilter)
    search_fields = (
        'country__name',
        'types_of_sanctions__name',
    )


@method_decorator(name='retrieve', decorator=swagger_auto_schema(tags=['sanctions']))
@method_decorator(name='list', decorator=swagger_auto_schema(tags=['sanctions']))
class PersonSanctionViewSet(RegisterViewMixin,
                            CachedViewSetMixin,
                            viewsets.ReadOnlyModelViewSet):
    permission_classes = [FreeForPayedProjects]
    queryset = PersonSanction.objects.all()
    serializer_class = PersonSanctionSerializer
    filter_backends = (DODjangoFilterBackend, SearchFilter)
    filterset_class = PersonSanctionFilterSet
    search_fields = (
        'full_name',
        'full_name_original',
        'taxpayer_number',
        'address',
        'place_of_birth',
        'types_of_sanctions__name',
        'occupation',
        'countries_of_citizenship__name'
    )


@method_decorator(name='retrieve', decorator=swagger_auto_schema(tags=['sanctions']))
@method_decorator(name='list', decorator=swagger_auto_schema(tags=['sanctions']))
class CompanySanctionViewSet(RegisterViewMixin,
                             CachedViewSetMixin,
                             viewsets.ReadOnlyModelViewSet):
    permission_classes = [FreeForPayedProjects]
    queryset = CompanySanction.objects.all()
    serializer_class = CompanySanctionSerializer
    filter_backends = (DODjangoFilterBackend, SearchFilter)
    filterset_class = CompanySanctionFilterSet
    search_fields = (
        'name',
        'name_original',
        'registration_number',
        'taxpayer_number',
        'address',
        'types_of_sanctions__name',
    )
