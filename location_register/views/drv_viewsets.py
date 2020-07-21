from data_ocean.views import CachedViewMixin
from location_register.models.drv_models import DrvBuilding
from location_register.serializers.drv_serializers import DrvBuildingSerializer
from rest_framework import generics, viewsets


class DrvBuildingViewSet(CachedViewMixin, viewsets.ReadOnlyModelViewSet):
    queryset = DrvBuilding.objects.order_by('code')
    serializer_class = DrvBuildingSerializer

   