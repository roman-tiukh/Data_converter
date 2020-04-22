from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from ratu.models.ratu_models import Region, District, City, Citydistrict, Street
from ratu.serializers.ratu_serializers import RegionSerializer, CitySerializer, CitydistrictSerializer, StreetSerializer, DistrictSerializer

class RegionView(APIView):
    def get(self, request):
        region = Region.objects.all()
        serializer = RegionSerializer(region, many=True)
        return Response({"region": serializer.data})

class DistrictView(APIView):
    def get(self, request):
        district = District.objects.all()
        serializer = DistrictSerializer(district, many=True)
        return Response({"district": serializer.data})

class CityView(APIView):
    def get(self, request):
        city = City.objects.all()
        serializer = CitySerializer(city, many=True)
        return Response({"city": serializer.data})

class CitydistrictView(APIView):
    def get(self, request):
        citydistrict = Citydistrict.objects.all()
        serializer = CitydistrictSerializer(citydistrict, many=True)
        return Response({"citydistrict": serializer.data})

class StreetView(APIView):
    def get(self, request):
        street = Street.objects.all()
        serializer = StreetSerializer(street, many=True)
        return Response({"street": serializer.data})