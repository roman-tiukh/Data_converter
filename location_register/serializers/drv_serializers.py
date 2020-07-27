from rest_framework import serializers

from location_register.models.drv_models import DrvBuilding


class DrvBuildingSerializer(serializers.Serializer):
    region = serializers.StringRelatedField()
    district = serializers.StringRelatedField()
    council = serializers.StringRelatedField()
    ato = serializers.StringRelatedField()
    street = serializers.StringRelatedField()
    zip_code = serializers.StringRelatedField()
    code = serializers.CharField()
    number = serializers.CharField()

    class Meta:
        model = DrvBuilding
        fields = ('id', 'region', 'district', 'council', 'ato', 'street', 'zip_code', 'code',
                  'number')
