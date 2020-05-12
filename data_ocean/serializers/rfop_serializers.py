from rest_framework import serializers
from data_ocean.models.rfop_models import FopToKved, ExchangeData, Fop
from data_ocean.serializers.kved_serializers import KvedSerializer
from data_ocean.serializers.common_serializers import (StatusSerializer, AuthoritySerializer,
TaxpayerTypeSerializer)

class RfopSerializer(serializers.Serializer):
    state = serializers.CharField(max_length=100)
    kved = serializers.CharField()
    fullname = serializers.CharField()
    address = serializers.CharField()

class ExchangeDataSerializer(serializers.ModelSerializer):
    authority = serializers.CharField(max_length=500)
    taxpayer_type = serializers.CharField(max_length=200)
    class Meta:
        model = ExchangeData
        fields = ['authority', 'taxpayer_type', 'start_date', 'start_number', 'end_date', 
        'end_number']

class FopSerializer(serializers.Serializer):
    fullname = serializers.CharField(max_length=100)
    address = serializers.CharField(max_length=500)
    status = StatusSerializer()
    registration_date = serializers.DateField()
    registration_info = serializers.CharField(max_length=300)
    estate_manager = serializers.CharField(max_length=100)
    termination_date = serializers.DateField()
    terminated_info = serializers.CharField(max_length=300)
    termination_cancel_info = serializers.CharField(max_length=100)
    contact_info = serializers.CharField(max_length=100)
    vp_dates = serializers.CharField(max_length=100)
    authority = AuthoritySerializer()
    kveds = serializers.StringRelatedField(many=True)
    exchange_data = ExchangeDataSerializer(many=True)