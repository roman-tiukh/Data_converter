from rest_framework import serializers
from data_ocean.models.ratu_models import Region, District, City, Citydistrict, Street

class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = '__all__'

class DistrictSerializer(serializers.ModelSerializer):
    region = serializers.CharField(max_length=30)
    class Meta:
        model = District
        fields = '__all__'
        
class CitySerializer(serializers.ModelSerializer):
    region = serializers.CharField(max_length=30)
    district = serializers.CharField(max_length=100)
    class Meta:
        model = City
        fields = '__all__'
    
class CitydistrictSerializer(serializers.ModelSerializer):
    region = serializers.CharField(max_length=30)
    district = serializers.CharField(max_length=100)
    city = serializers.CharField(max_length=100)
    class Meta:
        model = Citydistrict
        fields = '__all__'
    
class StreetSerializer(serializers.ModelSerializer):
    region = serializers.CharField(max_length=30)
    district = serializers.CharField(max_length=100)
    city = serializers.CharField(max_length=100)
    citydistrict = serializers.CharField(max_length=100)
    class Meta:
        model = Street
        fields = '__all__'