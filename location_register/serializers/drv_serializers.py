from rest_framework import serializers

from location_register.models.drv_models import DrvBuilding


class DrvBuildingSerializer(serializers.Serializer):

    region = serializers.CharField()
    district = serializers.CharField()
    council = serializers.CharField()
    ato = serializers.CharField()
    street = serializers.CharField()
    zip_code = serializers.CharField()
    code = serializers.CharField()
    number = serializers.CharField() 
