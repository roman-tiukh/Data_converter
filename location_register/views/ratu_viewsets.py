from django.shortcuts import get_object_or_404
from data_ocean.views import CachedViewMixin
from location_register.models.ratu_models import Region, District, City, Citydistrict, Street
from location_register.serializers.ratu_serializers import RegionSerializer, DistrictSerializer, CitySerializer, CitydistrictSerializer, \
    StreetSerializer
from rest_framework import viewsets
from rest_framework.response import Response


class RegionView(CachedViewMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    
class DistrictView(CachedViewMixin, viewsets.ReadOnlyModelViewSet):
    queryset = District.objects.all()
    serializer_class = DistrictSerializer

class CityView(CachedViewMixin, viewsets.ReadOnlyModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer

class CitydistrictView(CachedViewMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Citydistrict.objects.all()
    serializer_class = CitydistrictSerializer
    
class StreetView(CachedViewMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Street.objects.all()
    serializer_class = StreetSerializer

