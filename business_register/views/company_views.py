from django.shortcuts import get_object_or_404
from rest_framework import generics, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from business_register.models.company_models import Company
from business_register.serializers.company_serializers import CompanySerializer


class CompanyView(viewsets.ReadOnlyModelViewSet, PageNumberPagination):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

    def list(self, request):
        queryset = self.get_queryset()
        results = self.paginate_queryset(queryset)
        serializer = CompanySerializer(results, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        company = get_object_or_404(queryset, pk=pk)
        serializer = CompanySerializer(company)
        return Response(serializer.data)