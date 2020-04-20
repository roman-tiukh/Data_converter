from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from ratu.models.rfop_models import Rfop
from ratu.models.ruo_models import Ruo
from ratu.serializers import RfopSerializer
from ratu.serializers import RuoSerializer
from ratu.models.ratu_models import Region,District,City,Citydistrict,Street
from .serializers import RegionSerializer,CitySerializer,CitydistrictSerializer,StreetSerializer,DistrictSerializer

def index(request):
    return HttpResponse("Hello, world. You're at the ratu index.")

class RfopView(APIView):
    def get(self, request):
        rfop = Rfop.objects.all()[:5]
        serializer = RfopSerializer(rfop, many=True)
        return Response({"rfop": serializer.data})

class RuoView(APIView):
    def get(self, request):
        ruo = Ruo.objects.all()[:5]
        serializer = RuoSerializer(ruo, many=True)
        return Response({"ruo": serializer.data})

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




