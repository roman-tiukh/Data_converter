from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from location_register.models.drv_models import DrvBuilding
from location_register.serializers.drv_serializers import DrvBuildingSerializer
from rest_framework import generics, viewsets
from rest_framework.pagination import PageNumberPagination
from .ratu_viewsets import CachedViewMixin


<<<<<<< HEAD
class DrvBuildingViewSet(viewsets.ReadOnlyModelViewSet):
=======
class DrvBuildingViewSet(CachedViewMixin,viewsets.ReadOnlyModelViewSet):
    pagination_class = PageNumberPagination
>>>>>>> add cache to location_register
    queryset = DrvBuilding.objects.all()
    serializer_class = DrvBuildingSerializer

    