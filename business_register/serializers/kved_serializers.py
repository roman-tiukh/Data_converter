from rest_framework import serializers
from drf_dynamic_fields import DynamicFieldsMixin

from business_register.models.kved_models import Kved


class KvedDetailSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    group = serializers.StringRelatedField(help_text=Kved._meta.get_field('group').help_text)
    division = serializers.StringRelatedField(help_text=Kved._meta.get_field('division').help_text)
    section = serializers.StringRelatedField(help_text=Kved._meta.get_field('section').help_text)
    id = serializers.IntegerField(help_text='DataOcean\'s internal unique identifier of the object (NACE)')

    class Meta:
        model = Kved
        fields = ['id', 'code', 'name', 'group', 'division', 'section']
