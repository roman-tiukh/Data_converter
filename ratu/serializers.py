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

