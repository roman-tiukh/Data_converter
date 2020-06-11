<<<<<<< HEAD
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response
=======
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
>>>>>>> add cache to location_register
from location_register.models.ratu_models import Region, District, City, Citydistrict, Street
from location_register.serializers.ratu_serializers import RegionSerializer, DistrictSerializer, CitySerializer, CitydistrictSerializer, \
    StreetSerializer
from rest_framework import generics, viewsets
from rest_framework.pagination import PageNumberPagination


<<<<<<< HEAD
class RegionView(viewsets.ReadOnlyModelViewSet):
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


class DistrictView(viewsets.ReadOnlyModelViewSet):
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


class CityView(viewsets.ReadOnlyModelViewSet):
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


class CitydistrictView(viewsets.ReadOnlyModelViewSet):
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


class StreetView(viewsets.ReadOnlyModelViewSet):
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
=======
class CachedViewMixin:
    @method_decorator(cache_page(60*15))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
class RegionView(CachedViewMixin,viewsets.ReadOnlyModelViewSet):
    pagination_class = PageNumberPagination
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    
class DistrictView(CachedViewMixin, viewsets.ReadOnlyModelViewSet):
    pagination_class = PageNumberPagination
    queryset = District.objects.all()
    serializer_class = DistrictSerializer

class CityView(CachedViewMixin, viewsets.ReadOnlyModelViewSet):
    pagination_class = PageNumberPagination
    queryset = City.objects.all()
    serializer_class = CitySerializer

class CitydistrictView(CachedViewMixin, viewsets.ReadOnlyModelViewSet):
    pagination_class = PageNumberPagination
    queryset = Citydistrict.objects.all()
    serializer_class = CitydistrictSerializer
    
class StreetView(CachedViewMixin, viewsets.ReadOnlyModelViewSet):
    pagination_class = PageNumberPagination
    queryset = Street.objects.all()
    serializer_class = StreetSerializer

>>>>>>> add cache to location_register
