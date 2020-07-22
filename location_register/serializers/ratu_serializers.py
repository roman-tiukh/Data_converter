from rest_framework import serializers
from location_register.models.ratu_models import RatuRegion, RatuDistrict, RatuCity, RatuCityDistrict, RatuStreet


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RatuRegion
        fields = ('id', 'name', 'koatuu')


class DistrictSerializer(serializers.ModelSerializer):
    region = serializers.CharField(max_length=30)

    class Meta:
        model = RatuDistrict
        fields = ('id', 'region', 'name', 'koatuu')


class CitySerializer(serializers.ModelSerializer):
    region = serializers.CharField(max_length=30)
    district = serializers.CharField(max_length=100)

    class Meta:
        model = RatuCity
        fields = ('id', 'region', 'district', 'name', 'koatuu')


class CityDistrictSerializer(serializers.ModelSerializer):
    region = serializers.CharField(max_length=30)
    district = serializers.CharField(max_length=100)
    city = serializers.CharField(max_length=100)

    class Meta:
        model = RatuCityDistrict
        fields = ('id', 'region', 'district', 'city', 'name', 'koatuu')


class StreetSerializer(serializers.ModelSerializer):
    region = serializers.CharField(max_length=30)
    district = serializers.CharField(max_length=100)
    city = serializers.CharField(max_length=100)
    citydistrict = serializers.CharField(max_length=100)

    class Meta:
        model = RatuStreet
        fields = ('id', 'region', 'district', 'citydistrict', 'city', 'name')