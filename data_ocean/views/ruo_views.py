from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.response import Response
from data_ocean.models.ruo_models import Ruo
from data_ocean.serializers.ruo_serializers import RuoSerializer
from data_converter.pagination import CustomPagination
from data_ocean.views.views import Views

class RuoView(Views):
    serializer_class = RuoSerializer
    queryset = Ruo.objects.all()
    serializer = RuoSerializer(queryset, many=True)
    pagination_class = CustomPagination