from django.shortcuts import get_object_or_404, render
from rest_framework import generics, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from business_register.models.rfop_models import Rfop, Fop
from business_register.serializers.rfop_serializers import RfopSerializer, FopSerializer


class RfopView(viewsets.ReadOnlyModelViewSet, PageNumberPagination):
    queryset = Rfop.objects.all()

    def list(self, request):
        queryset = self.get_queryset()
        results = self.paginate_queryset(queryset)
        serializer = RfopSerializer(results, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        rfop = get_object_or_404(queryset, pk=pk)
        serializer = RfopSerializer(rfop)
        return Response(serializer.data)


class FopView(viewsets.ReadOnlyModelViewSet, PageNumberPagination):
    queryset = Fop.objects.all()
    serializer_class = FopSerializer

    def list(self, request):
        queryset = self.get_queryset()
        results = self.paginate_queryset(queryset)
        serializer = FopSerializer(results, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        fop = get_object_or_404(queryset, pk=pk)
        serializer = FopSerializer(fop)
        return Response(serializer.data)