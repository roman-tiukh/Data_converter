from django.shortcuts import get_object_or_404
from rest_framework import generics, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from business_register.models.kved_models import Kved
from business_register.serializers.kved_serializers import KvedDetailSerializer


class KvedView(viewsets.ReadOnlyModelViewSet, PageNumberPagination):
    queryset = Kved.objects.exclude(code='EMP')
    serializer_class = KvedDetailSerializer

    def list(self, request):
        queryset = self.get_queryset()
        results = self.paginate_queryset(queryset)
        serializer = KvedDetailSerializer(results, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        kved = get_object_or_404(queryset, pk=pk)
        serializer = KvedDetailSerializer(kved)
        return Response(serializer.data)