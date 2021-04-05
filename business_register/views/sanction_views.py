from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.filters import SearchFilter

from business_register.models.sanction_models import Sanction
from business_register.serializers.sanction_serializers import (
    SanctionSerializer
)
from data_converter.filter import DODjangoFilterBackend
from data_ocean.views import CachedViewSetMixin, RegisterViewMixin


@method_decorator(name='retrieve', decorator=swagger_auto_schema(tags=['sanction']))
@method_decorator(name='list', decorator=swagger_auto_schema(tags=['sanction']))
class SanctionViewSet(RegisterViewMixin,
                      CachedViewSetMixin,
                      viewsets.ReadOnlyModelViewSet):
    permission_classes = [RegisterViewMixin.permission_classes[0]]
    queryset = Sanction.objects.all()
    serializer_class = SanctionSerializer
    filter_backends = (DODjangoFilterBackend, SearchFilter)
    search_fields = (
        'name',
        'object_origin_name',
        'registration_number',
        'taxpayer_number',
        'address',
        'place_of_birth',
        'types_of_sanctions__name',
        'position',
        'country__name'
    )
