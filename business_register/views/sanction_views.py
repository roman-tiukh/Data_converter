from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.filters import SearchFilter

from business_register.models.sanction_models import PersonSanction, CompanySanction, CountrySanction
from business_register.serializers.sanction_serializers import (
    CountrySanctionSerializer, PersonSanctionSerializer, CompanySanctionSerializer
)
from data_converter.filter import DODjangoFilterBackend
from data_ocean.views import CachedViewSetMixin, RegisterViewMixin


@method_decorator(name='retrieve', decorator=swagger_auto_schema(tags=['sanction_country']))
@method_decorator(name='list', decorator=swagger_auto_schema(tags=['sanction_country']))
class CountrySanctionViewSet(RegisterViewMixin,
                             CachedViewSetMixin,
                             viewsets.ReadOnlyModelViewSet):
    queryset = CountrySanction.objects.all()
    serializer_class = CountrySanctionSerializer
    filter_backends = (DODjangoFilterBackend, SearchFilter)
    search_fields = (
        'country__name',
        'types_of_sanctions__name',
    )


@method_decorator(name='retrieve', decorator=swagger_auto_schema(tags=['sanction_person']))
@method_decorator(name='list', decorator=swagger_auto_schema(tags=['sanction_person']))
class PersonSanctionViewSet(RegisterViewMixin,
                            CachedViewSetMixin,
                            viewsets.ReadOnlyModelViewSet):
    queryset = PersonSanction.objects.all()
    serializer_class = PersonSanctionSerializer
    filter_backends = (DODjangoFilterBackend, SearchFilter)
    search_fields = (
        'full_name',
        'full_name_original_transcription',
        'taxpayer_number',
        'address',
        'place_of_birth',
        'types_of_sanctions__name',
        'position',
        'countries_of_citizenship__name'
    )


@method_decorator(name='retrieve', decorator=swagger_auto_schema(tags=['sanction_company']))
@method_decorator(name='list', decorator=swagger_auto_schema(tags=['sanction_company']))
class CompanySanctionViewSet(RegisterViewMixin,
                             CachedViewSetMixin,
                             viewsets.ReadOnlyModelViewSet):
    queryset = CompanySanction.objects.all()
    serializer_class = CompanySanctionSerializer
    filter_backends = (DODjangoFilterBackend, SearchFilter)
    search_fields = (
        'name',
        'name_original_transcription',
        'number',
        'address',
        'types_of_sanctions__name',
        'country_of_registration__name'
    )
