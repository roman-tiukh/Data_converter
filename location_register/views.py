from django.shortcuts import get_object_or_404
from rest_framework import generics, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from location_register.models import Region, District, City, Citydistrict, Street
from location_register.serializers import RegionSerializer, DistrictSerializer, CitySerializer, CitydistrictSerializer, \
    StreetSerializer


class RegionView(viewsets.ReadOnlyModelViewSet, PageNumberPagination):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer

    def list(self, request):
        queryset = self.get_queryset()
        results = self.paginate_queryset(queryset)
        serializer = RegionSerializer(results, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        region = get_object_or_404(queryset, pk=pk)
        serializer = RegionSerializer(region)
        return Response(serializer.data)


class DistrictView(viewsets.ReadOnlyModelViewSet, PageNumberPagination):
    queryset = District.objects.all()
    serializer_class = DistrictSerializer

    def list(self, request):
        queryset = self.get_queryset()
        results = self.paginate_queryset(queryset)
        serializer = DistrictSerializer(results, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        district = get_object_or_404(queryset, pk=pk)
        serializer = DistrictSerializer(district)
        return Response(serializer.data)


class CityView(viewsets.ReadOnlyModelViewSet, PageNumberPagination):
    queryset = City.objects.all()
    serializer_class = CitySerializer

    def list(self, request):
        queryset = self.get_queryset()
        results = self.paginate_queryset(queryset)
        serializer = CitySerializer(results, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        city = get_object_or_404(queryset, pk=pk)
        serializer = CitySerializer(city)
        return Response(serializer.data)


class CitydistrictView(viewsets.ReadOnlyModelViewSet, PageNumberPagination):
    queryset = Citydistrict.objects.all()
    serializer_class = CitydistrictSerializer

    def list(self, request):
        queryset = self.get_queryset()
        results = self.paginate_queryset(queryset)
        serializer = CitydistrictSerializer(results, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        citydistrict = get_object_or_404(queryset, pk=pk)
        serializer = CitydistrictSerializer(citydistrict)
        return Response(serializer.data)


class StreetView(viewsets.ReadOnlyModelViewSet, PageNumberPagination):
    queryset = Street.objects.all()
    serializer_class = StreetSerializer

    def list(self, request):
        queryset = self.get_queryset()
        results = self.paginate_queryset(queryset)
        serializer = StreetSerializer(results, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        street = get_object_or_404(queryset, pk=pk)
        serializer = StreetSerializer(street)
        return Response(serializer.data)