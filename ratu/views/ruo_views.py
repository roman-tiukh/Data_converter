from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from ratu.models.ruo_models import Ruo
from ratu.serializers.ruo_serializers import RuoSerializer

class RuoView(APIView):
    def get(self, request):
        ruo = Ruo.objects.all()[:5]
        serializer = RuoSerializer(ruo, many=True)
        return Response({"ruo": serializer.data})