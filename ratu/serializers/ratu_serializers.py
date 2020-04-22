from rest_framework import serializers

class RegionSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    koatuu = serializers.CharField()
    
class DistrictSerializer(serializers.Serializer):
    region_id = serializers.IntegerField()
    name = serializers.CharField(max_length=100)
    koatuu = serializers.CharField()
    
class CitySerializer(serializers.Serializer):
    region_id = serializers.IntegerField()
    district_id = serializers.IntegerField()
    name = serializers.CharField(max_length=100)
    koatuu = serializers.CharField()

class CitydistrictSerializer(serializers.Serializer):
    region_id = serializers.IntegerField()
    district_id = serializers.IntegerField()
    city_id = serializers.IntegerField()
    name = serializers.CharField(max_length=100)
    koatuu = serializers.CharField()
    
class StreetSerializer(serializers.Serializer):
    region_id = serializers.IntegerField()
    district_id = serializers.IntegerField()
    city_id = serializers.IntegerField()
    citydistrict_id = serializers.IntegerField()
    name = serializers.CharField(max_length=100)