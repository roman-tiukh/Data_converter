from rest_framework import serializers
from data_ocean.models.kved_models import Kved

class KvedSerializerWithModel(serializers.ModelSerializer):
    class Meta:
        model = Kved
        fields = ['code', 'name', 'group', 'division', 'section']