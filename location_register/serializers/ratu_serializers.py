from rest_framework import serializers
from location_register.models.ratu_models import RatuRegion, RatuDistrict, RatuCity, RatuCityDistrict, RatuStreet


class RatuRegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RatuRegion
        fields = ('id', 'name', 'koatuu')


class RatuDistrictSerializer(serializers.ModelSerializer):
    region = serializers.StringRelatedField()

    class Meta:
        model = RatuDistrict
        fields = ('id', 'region', 'name', 'koatuu')


class RatuCitySerializer(serializers.ModelSerializer):
    region = serializers.StringRelatedField()
    district = serializers.StringRelatedField()

    class Meta:
        model = RatuCity
        fields = ('id', 'region', 'district', 'name', 'koatuu')


class RatuCityDistrictSerializer(serializers.ModelSerializer):
    region = serializers.StringRelatedField()
    district = serializers.StringRelatedField()
    city = serializers.StringRelatedField()

    class Meta:
        model = RatuCityDistrict
        fields = ('id', 'region', 'district', 'city', 'name', 'koatuu')


class RatuStreetSerializer(serializers.ModelSerializer):
    region = serializers.StringRelatedField()
    district = serializers.StringRelatedField()
    city = serializers.StringRelatedField()
    citydistrict = serializers.StringRelatedField()

    class Meta:
        model = RatuStreet
        fields = ('id', 'region', 'district', 'citydistrict', 'city', 'name')
