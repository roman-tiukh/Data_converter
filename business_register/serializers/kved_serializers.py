from rest_framework import serializers

from business_register.models.kved_models import Kved


class KvedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kved
        fields = ['code', 'name']


class KvedDetailSerializer(serializers.ModelSerializer):
    group = serializers.CharField(max_length=500)
    division = serializers.CharField(max_length=500)
    section = serializers.CharField(max_length=500)

    class Meta:
        model = Kved
        fields = ['code', 'name', 'group', 'division', 'section']