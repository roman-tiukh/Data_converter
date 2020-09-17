from rest_framework import serializers

from location_register.models.koatuu_models import (
    KoatuuFirstLevel, KoatuuSecondLevel,
    KoatuuThirdLevel, KoatuuFourthLevel,
)
from drf_dynamic_fields import DynamicFieldsMixin


class KoatuuFourthLevelSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    first_level = serializers.StringRelatedField()
    second_level = serializers.StringRelatedField()
    third_level = serializers.StringRelatedField()
    category = serializers.StringRelatedField()

    class Meta:
        model = KoatuuFourthLevel
        fields = (
            'id', 'code', 'name', 'category',
            'first_level', 'second_level', 'third_level'
        )


class KoatuuThirdLevelSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    first_level = serializers.StringRelatedField()
    second_level = serializers.StringRelatedField()
    category = serializers.StringRelatedField()
    fourth_level_places = KoatuuFourthLevelSerializer(many=True)

    class Meta:
        model = KoatuuThirdLevel
        fields = (
            'id', 'code', 'name', 'category', 'first_level',
            'second_level', 'fourth_level_places'
        )


class KoatuuSecondLevelSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    first_level = serializers.StringRelatedField()
    category = serializers.StringRelatedField()
    third_level_places = KoatuuThirdLevelSerializer(many=True)

    class Meta:
        model = KoatuuSecondLevel
        fields = (
            'id', 'code', 'name', 'category', 'first_level',
            'third_level_places',
        )


class KoatuuFirstLevelSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    second_level_places = KoatuuSecondLevelSerializer(many=True)

    class Meta:
        model = KoatuuFirstLevel
        fields = ('id', 'code', 'name', 'second_level_places')
