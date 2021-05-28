from drf_dynamic_fields import DynamicFieldsMixin
from rest_framework import serializers
from location_register.models.address_models import Country


class CountrySerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    name_en = serializers.CharField(source='name')

    class Meta:
        model = Country
        fields = ('name_en', 'name_uk')
