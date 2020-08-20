from rest_framework import serializers

from location_register.models.koatuu_models import (KoatuuFirstLevel, KoatuuSecondLevel,
                                                    KoatuuThirdLevel, KoatuuFourthLevel)


class KoatuuFourthLevelSerializer(serializers.ModelSerializer):
    first_level = serializers.StringRelatedField()
    second_level = serializers.StringRelatedField()
    third_level = serializers.StringRelatedField()
    category = serializers.StringRelatedField()

    class Meta:
        model = KoatuuFourthLevel
        fields = ('code', 'name', 'category', 'first_level', 'second_level', 'third_level')


class KoatuuThirdLevelSerializer(serializers.ModelSerializer):
    first_level = serializers.StringRelatedField()
    second_level = serializers.StringRelatedField()
    category = serializers.StringRelatedField()
    fourth_level_places = KoatuuFourthLevelSerializer(many=True)

    class Meta:
        model = KoatuuThirdLevel
        fields = ('code', 'name', 'category', 'first_level', 'second_level', 'fourth_level_places')


class KoatuuSecondLevelSerializer(serializers.ModelSerializer):
    first_level = serializers.StringRelatedField()
    category = serializers.StringRelatedField()
    third_level_places = KoatuuThirdLevelSerializer(many=True)

    class Meta:
        model = KoatuuSecondLevel
        fields = ('code', 'name', 'category', 'first_level', 'third_level_places')


class KoatuuFirstLevelSerializer(serializers.ModelSerializer):
    second_level_places = KoatuuSecondLevelSerializer(many=True)

    class Meta:
        model = KoatuuFirstLevel
        fields = ('code', 'name', 'second_level_places')
