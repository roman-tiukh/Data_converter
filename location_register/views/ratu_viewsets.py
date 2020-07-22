from django.shortcuts import get_object_or_404
from data_ocean.views import CachedViewMixin
from location_register.models.ratu_models import RatuRegion, RatuDistrict, RatuCity, RatuCityDistrict, RatuStreet
from location_register.serializers.ratu_serializers import RegionSerializer, DistrictSerializer, CitySerializer, CityDistrictSerializer, \
    StreetSerializer
from rest_framework import viewsets
from rest_framework.response import Response


class RegionView(CachedViewMixin, viewsets.ReadOnlyModelViewSet):
    queryset = RatuRegion.objects.all()
    serializer_class = RegionSerializer
    
class DistrictView(CachedViewMixin, viewsets.ReadOnlyModelViewSet):
    queryset = RatuDistrict.objects.all()
    serializer_class = DistrictSerializer

class CityView(CachedViewMixin, viewsets.ReadOnlyModelViewSet):
    queryset = RatuCity.objects.all()
    serializer_class = CitySerializer

class CityDistrictView(CachedViewMixin, viewsets.ReadOnlyModelViewSet):
    queryset = RatuCityDistrict.objects.all()
    serializer_class = CityDistrictSerializer
    
class StreetView(CachedViewMixin, viewsets.ReadOnlyModelViewSet):
    queryset = RatuStreet.objects.all()
    serializer_class = StreetSerializer

