from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from rest_framework import generics, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from data_converter.pagination import CustomPagination
from data_ocean.models.rfop_models import Fop, Rfop
from data_ocean.serializers.rfop_serializers import (FopSerializer, RfopSerializer)
from data_ocean.views.views import Views


class RfopView(Views):
    serializer_class = RfopSerializer
    queryset = Rfop.objects.all()
    serializer = RfopSerializer(queryset, many=True)
    pagination_class = CustomPagination
    
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