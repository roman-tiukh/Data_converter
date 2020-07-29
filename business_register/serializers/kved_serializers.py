from rest_framework import serializers

from business_register.models.kved_models import Kved


class KvedDetailSerializer(serializers.ModelSerializer):
    group = serializers.StringRelatedField()
    division = serializers.StringRelatedField()
    section = serializers.StringRelatedField()

    class Meta:
        model = Kved
        fields = ['id', 'code', 'name', 'group', 'division', 'section']
