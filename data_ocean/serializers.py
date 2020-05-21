from rest_framework import serializers

from data_ocean.models import Status, Authority, TaxpayerType


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ['name']


class AuthoritySerializer(serializers.ModelSerializer):
    class Meta:
        model = Authority
        fields = ['name', 'code']


class TaxpayerTypeSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=200)
    class Meta:
        model = TaxpayerType
        fields = ['name']