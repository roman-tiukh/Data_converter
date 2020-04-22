from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from ratu.models.rfop_models import Rfop
from ratu.serializers.rfop_serializers import RfopSerializer

class RfopView(APIView):
    def get(self, request):
        rfop = Rfop.objects.all()[:5]
        serializer = RfopSerializer(rfop, many=True)
        return Response({"rfop": serializer.data})