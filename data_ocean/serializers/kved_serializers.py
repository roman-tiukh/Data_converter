from rest_framework import serializers
from data_ocean.models.kved_models import Kved, Group, Division, Section

class KvedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kved
        fields = ['code', 'name']

class FullKvedSerializer(serializers.ModelSerializer):
    group = serializers.CharField(max_length=500)
    division = serializers.CharField(max_length=500)    
    section = serializers.CharField(max_length=500)
    
    class Meta:
        model = Kved
        fields = ['code', 'name', 'group', 'division', 'section']