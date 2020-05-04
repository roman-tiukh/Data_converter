from rest_framework import serializers
from data_ocean.models.kved_models import Kved

class KvedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kved
        fields = ['code', 'name']