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
    title = serializers.CharField(max_length=120)
    description = serializers.CharField()
    body = serializers.CharField()

class DistrictSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=120)
    description = serializers.CharField()
    body = serializers.CharField()

class CitySerializer(serializers.Serializer):
    title = serializers.CharField(max_length=120)
    description = serializers.CharField()
    body = serializers.CharField()

class CitydistrictSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=120)
    description = serializers.CharField()
    body = serializers.CharField()

class StreetSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=120)
    description = serializers.CharField()
    body = serializers.CharField()

