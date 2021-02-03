from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import SearchFilter

from data_ocean.views import CachedViewSetMixin, RegisterViewMixin
from location_register.filters import DrvBuildingFilterSet
from location_register.models.drv_models import DrvBuilding
from location_register.serializers.drv_serializers import DrvBuildingSerializer


class DrvBuildingViewSet(RegisterViewMixin,
                         CachedViewSetMixin,
                         viewsets.ReadOnlyModelViewSet):
    queryset = DrvBuilding.objects.select_related(
        'region', 'district', 'council', 'ato', 'street', 'zip_code',
    ).all()
    serializer_class = DrvBuildingSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset = DrvBuildingFilterSet
    search_fields = ('code', 'number')
