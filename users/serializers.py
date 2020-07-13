from rest_framework.authtoken.models import Token
from rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers
from rest_auth.serializers import LoginSerializer, PasswordResetSerializer
from django.utils.translation import ugettext_lazy as _
from difflib import SequenceMatcher
from .forms import CustomPasswordResetForm
from .models import DataOceanUser


class DataOceanUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataOceanUser
        fields = ('id', 'last_name', 'first_name', 'email', 'organization', 'position', 'date_of_birth')


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

    def validate(self, data):
        super(CustomRegisterSerializer, self).validate(data)

        # Custom Similarity Validator

        max_similarity = 0.7
        cmp_attrs = {
            'email': 'Email',
            'first_name': _('First Name'),
            'last_name': _('Last Name'),
        }

        for (k, v) in cmp_attrs.items():
            if SequenceMatcher(a=data['password1'].lower(), b=data[k].lower()).quick_ratio() >= max_similarity:
                err_msg = _('Your password can’t be too similar to your ') + v + '.'
                raise serializers.ValidationError(err_msg)

        return data


class CustomLoginSerializer(LoginSerializer):
    username = None


class TokenSerializer(serializers.ModelSerializer):
    user = DataOceanUserSerializer()

    class Meta:
        model = Token
        fields = ('key', 'user')


class CustomPasswordResetSerializer(PasswordResetSerializer):
    password_reset_form_class = CustomPasswordResetForm
