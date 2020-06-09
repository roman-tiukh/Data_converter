from rest_framework import serializers
from users import models


class DataOceanUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DataOceanUser
        fields = ('email', )
