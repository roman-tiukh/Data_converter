from django.shortcuts import get_object_or_404
from data_ocean.views import CachedViewMixin
from location_register.models.ratu_models import Region, District, City, CityDistrict, Street
from location_register.serializers.ratu_serializers import RegionSerializer, DistrictSerializer, CitySerializer, CityDistrictSerializer, \
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

class CityDistrictView(CachedViewMixin, viewsets.ReadOnlyModelViewSet):
    queryset = CityDistrict.objects.all()
    serializer_class = CityDistrictSerializer
    
class StreetView(CachedViewMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Street.objects.all()
    serializer_class = StreetSerializer
