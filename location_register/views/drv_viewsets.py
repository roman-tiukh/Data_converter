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

    # def list(self, request):
    #     queryset = self.get_queryset()
    #     results = self.paginate_queryset(queryset)
    #     serializer = DrvBuildingSerializer(results, many=True)
    #     return self.get_paginated_response(serializer.data)

    # def retrieve(self, request, pk=None):
    #     queryset = self.get_queryset()
    #     region = get_object_or_404(queryset, pk=pk)
    #     serializer = DrvBuildingSerializer(region)
    #     return Response(serializer.data)
