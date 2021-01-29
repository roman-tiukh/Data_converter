from rest_framework import serializers

from data_ocean.models import Status, Authority, TaxpayerType, Register


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ['name']


class AuthoritySerializer(serializers.ModelSerializer):
    class Meta:
        model = Authority
        fields = ['id', 'name', 'code']


class TaxpayerTypeSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=200)

    class Meta:
        model = TaxpayerType
        fields = ['id', 'name']


class RegisterSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source='get_status_display')

    class Meta:
        model = Register
        fields = [
            'id',
            'name',
            'name_eng',
            'source_name',
            'source_url_address',
            'source_api_address',
            'source_register_id',
            'api_list',
            'api_detail',
            'status',
            'total_records'
        ]
