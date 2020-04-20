from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from ratu.models.rfop_models import Rfop
from ratu.models.ruo_models import Ruo
from ratu.serializers import RfopSerializer
from ratu.serializers import RuoSerializer

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
