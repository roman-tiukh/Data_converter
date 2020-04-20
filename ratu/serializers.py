from rest_framework import serializers

class RfopSerializer(serializers.Serializer):
    state = serializers.CharField(max_length=120)
    kved = serializers.CharField()
    fullname = serializers.CharField()
    address = serializers.CharField()

class RuoSerializer(serializers.Serializer):
    state = serializers.CharField(max_length=120)
    kved = serializers.CharField()
    name = serializers.CharField()
    short_name = serializers.CharField()
    edrpou = serializers.CharField()
    address = serializers.CharField()
    boss = serializers.CharField()

class RegionSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=120)
    koatuu = serializers.CharField()
    
class DistrictSerializer(serializers.Serializer):
    region_id = serializers.IntegerField()
    name = serializers.CharField(max_length=120)
    koatuu = serializers.CharField()
    
class CitySerializer(serializers.Serializer):
    region_id = serializers.IntegerField()
    district_id = serializers.IntegerField()
    name = serializers.CharField(max_length=120)
    koatuu = serializers.CharField()

class CitydistrictSerializer(serializers.Serializer):
    region_id = serializers.IntegerField()
    district_id = serializers.IntegerField()
    city_id = serializers.IntegerField()
    name = serializers.CharField(max_length=120)
    koatuu = serializers.CharField()
    
class StreetSerializer(serializers.Serializer):
    region_id = serializers.IntegerField()
    district_id = serializers.IntegerField()
    city_id = serializers.IntegerField()
    citydistrict_id = serializers.IntegerField()
    name = serializers.CharField(max_length=120)

    


