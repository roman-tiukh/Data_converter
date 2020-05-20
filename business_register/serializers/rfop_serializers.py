from rest_framework import serializers

from business_register.models.rfop_models import Rfop, ExchangeDataFop
from data_ocean.serializers import StatusSerializer, AuthoritySerializer


class RfopSerializer(serializers.Serializer):
    state = serializers.CharField(max_length=100)
    kved = serializers.CharField()

    class Meta:
        model = Rfop
        fields = ('id', 'state', 'kved', 'fullname', 'address')


class ExchangeDataFopSerializer(serializers.ModelSerializer):
    authority = serializers.CharField(max_length=500)
    taxpayer_type = serializers.CharField(max_length=200)

    class Meta:
        model = ExchangeDataFop
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
    exchange_data = ExchangeDataFopSerializer(many=True)