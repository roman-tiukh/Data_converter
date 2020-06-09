from django.shortcuts import get_object_or_404
from rest_framework import generics, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from location_register.models.drv_models import DrvBuilding
from location_register.serializers.drv_serializers import DrvBuildingSerializer


class DrvBuildingViewSet(viewsets.ReadOnlyModelViewSet, PageNumberPagination):
    queryset = DrvBuilding.objects.all()
    serializer_class = DrvBuildingSerializer

    def list(self, request):
        queryset = self.get_queryset()
        results = self.paginate_queryset(queryset)
        serializer = DrvBuildingSerializer(results, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        region = get_object_or_404(queryset, pk=pk)
        serializer = DrvBuildingSerializer(region)
        return Response(serializer.data)
