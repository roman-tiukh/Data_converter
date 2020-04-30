from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.response import Response
from ratu.models.ruo_models import Ruo
from ratu.serializers.ruo_serializers import RuoSerializer
from data_converter.pagination import CustomPagination
from ratu.views.views import Views

class RuoView(Views):
    serializer_class = RuoSerializer
    queryset = Ruo.objects.all()
    serializer = RuoSerializer(queryset, many=True)
    pagination_class = CustomPagination