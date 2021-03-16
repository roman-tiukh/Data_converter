from rest_framework import serializers
from location_register.models.ratu_models import RatuRegion, RatuDistrict, RatuCity, RatuCityDistrict, RatuStreet


class RatuRegionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(help_text='DataOcean\'s internal unique identifier of the object (RATU)')
    class Meta:
        model = RatuRegion
        fields = ('id', 'name', 'koatuu')


class RatuDistrictSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(help_text='DataOcean\'s internal unique identifier of the object (RATU)')
    region = serializers.StringRelatedField(help_text='The region to which the district belongs')

    class Meta:
        model = RatuDistrict
        fields = ('id', 'region', 'name', 'koatuu')


class RatuCitySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(help_text='DataOcean\'s internal unique identifier of the object (RATU)')
    region = serializers.StringRelatedField(help_text='The region to which the city belongs')
    district = serializers.StringRelatedField(help_text='The district to which the city belongs')

    class Meta:
        model = RatuCity
        fields = ('id', 'region', 'district', 'name', 'koatuu')


class RatuCityDistrictSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(help_text='DataOcean\'s internal unique identifier of the object (RATU)')
    region = serializers.StringRelatedField(help_text='The region to which the city belongs')
    district = serializers.StringRelatedField(help_text='The district of the region to which the city belongs')
    city = serializers.StringRelatedField(help_text='Name of the city in which the district is located')

    class Meta:
        model = RatuCityDistrict
        fields = ('id', 'region', 'district', 'city', 'name', 'koatuu')


class RatuStreetSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(help_text='DataOcean\'s internal unique identifier of the object (RATU)')
    region = serializers.StringRelatedField(help_text='The region to which the city belongs')
    district = serializers.StringRelatedField(help_text='The district of the region to which the city belongs')
    city = serializers.StringRelatedField(help_text='Name of the city where the street is located')
    citydistrict = serializers.StringRelatedField(help_text='Name of the district of the city where the street is located')

    class Meta:
        model = RatuStreet
        fields = ('id', 'region', 'district', 'citydistrict', 'city', 'name')
