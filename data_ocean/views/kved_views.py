from django.shortcuts import get_object_or_404
from rest_framework import generics, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from data_ocean.models.kved_models import Kved
from data_ocean.serializers.kved_serializers import FullKvedSerializer


class KvedView(viewsets.ReadOnlyModelViewSet, PageNumberPagination):
    queryset = Kved.objects.exclude(code='EMP')
    serializer_class = FullKvedSerializer

    def list(self, request):
        queryset = self.get_queryset()
        results = self.paginate_queryset(queryset)
        serializer = FullKvedSerializer(results, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        kved = get_object_or_404(queryset, pk=pk)
        serializer = FullKvedSerializer(kved)
        return Response(serializer.data)