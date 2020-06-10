from users import models
from rest_framework.authtoken.models import Token
from rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers
from rest_auth.serializers import LoginSerializer


class DataOceanUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DataOceanUser
        fields = ('id', 'last_name', 'first_name', 'email', )


class CustomRegisterSerializer(RegisterSerializer):
    username = None
    first_name = serializers.CharField(required=True, write_only=True)
    last_name = serializers.CharField(required=True, write_only=True)

    def get_cleaned_data(self):
        return {
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
            'email': self.validated_data.get('email', ''),
            'password1': self.validated_data.get('password1', ''),
            'password2': self.validated_data.get('password2', ''),
        }


class CustomLoginSerializer(LoginSerializer):
    username = None


class TokenSerializer(serializers.ModelSerializer):
    user = DataOceanUserSerializer()

    class Meta:
        model = Token
        fields = ('key', 'user')

