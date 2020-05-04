from rest_framework import serializers
from data_ocean.models.ratu_models import Region, District, City, Citydistrict, Street


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ('id', 'name', 'koatuu')
   
class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ('id', 'region', 'name', 'koatuu')
    
class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ('id', 'region', 'district', 'name', 'koatuu')
    
class CitydistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = Citydistrict
        fields = ('id', 'region', 'district', 'city', 'name', 'koatuu')
    serializers.CharField(max_length=10)
    
class StreetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Street
        fields = ('id', 'region', 'district', 'city', 'citydistrict', 'name')