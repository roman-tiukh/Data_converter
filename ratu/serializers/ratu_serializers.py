from rest_framework import serializers

class RegionSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    koatuu = serializers.CharField()
    
class DistrictSerializer(serializers.Serializer):
    region = serializers.CharField(max_length=100)
    name = serializers.CharField(max_length=100)
    koatuu = serializers.CharField()
    
class CitySerializer(serializers.Serializer):
    region = serializers.CharField(max_length=100)
    district = serializers.CharField(max_length=100)
    name = serializers.CharField(max_length=100)
    koatuu = serializers.CharField()

class CitydistrictSerializer(serializers.Serializer):
    region = serializers.CharField(max_length=100)
    district = serializers.CharField(max_length=100)
    city = serializers.CharField(max_length=100)
    name = serializers.CharField(max_length=100)
    koatuu = serializers.CharField()
    
class StreetSerializer(serializers.Serializer):
    region = serializers.CharField(max_length=100)
    district = serializers.CharField(max_length=100)
    city = serializers.CharField(max_length=100)
    citydistrict = serializers.CharField(max_length=100)
    name = serializers.CharField(max_length=100)