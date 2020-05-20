from rest_framework import serializers

from business_register.models.ruo_models import Founders


class FoundersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Founders
        fields = ['founder']


class RuoSerializer(serializers.Serializer):
    state = serializers.CharField(max_length=100)
    kved = serializers.CharField()
    name = serializers.CharField()
    short_name = serializers.CharField()
    edrpou = serializers.CharField()
    address = serializers.CharField()
    boss = serializers.CharField()
    founders = FoundersSerializer(many=True)