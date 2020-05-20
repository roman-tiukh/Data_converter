from django.shortcuts import get_object_or_404
from rest_framework import generics, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from business_register.models.ruo_models import Ruo
from business_register.serializers.ruo_serializers import RuoSerializer


class RuoView(viewsets.ReadOnlyModelViewSet, PageNumberPagination):
    queryset = Ruo.objects.all()
    serializer_class = RuoSerializer

    def list(self, request):
        queryset = self.get_queryset()
        results = self.paginate_queryset(queryset)
        serializer = RuoSerializer(results, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        ruo = get_object_or_404(queryset, pk=pk)
        serializer = RuoSerializer(ruo)
        return Response(serializer.data)