from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.response import Response
from ratu.models.rfop_models import Rfop
from ratu.serializers.rfop_serializers import RfopSerializer
from data_converter.pagination import CustomPagination
from ratu.views.views import Views

class RfopView(Views):
    serializer_class = RfopSerializer
    queryset = Rfop.objects.all()
    serializer = RfopSerializer(queryset, many=True)
    pagination_class = CustomPagination