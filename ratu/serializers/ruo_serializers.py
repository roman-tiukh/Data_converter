from rest_framework import serializers

class RuoSerializer(serializers.Serializer):
    state = serializers.CharField(max_length=100)
    kved = serializers.CharField()
    name = serializers.CharField()
    short_name = serializers.CharField()
    edrpou = serializers.CharField()
    address = serializers.CharField()
    boss = serializers.CharField()