from rest_framework import serializers

class RfopSerializer(serializers.Serializer):
    state = serializers.CharField(max_length=100)
    kved = serializers.CharField()
    fullname = serializers.CharField()
    address = serializers.CharField()
