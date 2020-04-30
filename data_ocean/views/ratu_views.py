from django.shortcuts import render
from django.http import HttpResponse
from data_ocean.models.ratu_models import Region, District, City, Citydistrict, Street
from data_ocean.serializers.ratu_serializers import RegionSerializer, CitySerializer, CitydistrictSerializer, StreetSerializer, DistrictSerializer
from data_ocean.views.views import Views
from data_converter.pagination import CustomPagination

class RegionView(Views):
    serializer_class = RegionSerializer
    queryset = Region.objects.all()
    serializer = RegionSerializer(queryset, many=True)
    pagination_class = CustomPagination

class DistrictView(Views):
    serializer_class = DistrictSerializer
    queryset = District.objects.all()
    serializer = DistrictSerializer(queryset, many=True)
    pagination_class = CustomPagination

class CityView(Views):
    serializer_class = CitySerializer
    queryset = City.objects.all()
    serializer = CitySerializer(queryset, many=True)
    pagination_class = CustomPagination

class CitydistrictView(Views):
    serializer_class = CitydistrictSerializer
    queryset = Citydistrict.objects.all()
    serializer = CitydistrictSerializer(queryset, many=True)
    pagination_class = CustomPagination

class StreetView(Views):
    serializer_class = StreetSerializer
    queryset = Street.objects.all()
    serializer = StreetSerializer(queryset, many=True)
    pagination_class = CustomPagination