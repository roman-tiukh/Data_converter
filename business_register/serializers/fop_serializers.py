from drf_dynamic_fields import DynamicFieldsMixin
from rest_framework import serializers

from business_register.models.fop_models import ExchangeDataFop, Fop
from data_ocean.serializers import StatusSerializer, AuthoritySerializer


class ExchangeDataFopSerializer(serializers.ModelSerializer):
    authority = serializers.CharField(max_length=500)
    taxpayer_type = serializers.CharField(max_length=200)

    class Meta:
        model = ExchangeDataFop
        fields = ['authority', 'taxpayer_type', 'start_date', 'start_number', 'end_date',
                  'end_number']


class FopSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    status = serializers.StringRelatedField()
    termination_date = serializers.DateField()
    authority = AuthoritySerializer()
    kveds = serializers.StringRelatedField(many=True)
    exchange_data = ExchangeDataFopSerializer(many=True)

    class Meta:
        model = Fop
        fields = [
            'fullname', 'address', 'status', 'registration_date', 'registration_info',
            'estate_manager', 'termination_date', 'terminated_info', 'termination_cancel_info',
            'contact_info', 'vp_dates', 'authority', 'kveds', 'exchange_data',
        ]
