from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework import generics
from rest_framework.response import Response
from data_ocean.models.kved_models import Kved
from data_ocean.serializers.kved_serializers import KvedSerializer
from rest_framework.pagination import PageNumberPagination

class KvedView(viewsets.ReadOnlyModelViewSet, PageNumberPagination):
    queryset = Kved.objects.all()
    serializer_class = KvedSerializer

    def list(self, request):
        queryset = self.get_queryset()
        results = self.paginate_queryset(queryset)
        serializer = KvedSerializer(results, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        kved = get_object_or_404(queryset, pk=pk)
        serializer = KvedSerializer(kved)
        return Response(serializer.data)