import re
from difflib import SequenceMatcher

from django.core.validators import RegexValidator
from django.utils.text import format_lazy
from django.utils.translation import ugettext_lazy as _
from rest_auth.registration.serializers import RegisterSerializer
from rest_auth.serializers import LoginSerializer, PasswordResetSerializer
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from .forms import CustomPasswordResetForm
from .models import DataOceanUser, Question, Notification
from .validators import name_symbols_validator, two_in_row_validator


class DataOceanUserSerializer(serializers.ModelSerializer):

    def validate(self, data):

        """validate fop and legal_entity fields"""

        if data.get('person_status') in ('individual_entrepreneur', 'legal_entity'):
            if not data.get('iban'):
              raise serializers.ValidationError({'iban':_(f"IBAN is required for %(person_status)s" % {
                  'person_status': data.get('person_status').replace('_', ' '),
              })})
        if data.get('person_status') == DataOceanUser.LEGAL_ENTITY:
            if not data.get('edrpou'):
                raise serializers.ValidationError({'edrpou':_("EDRPOU is required for Legal entity")})
            if not data.get('company_name'):
                raise serializers.ValidationError({'name_company':_("Company name is required for Legal entity")})
            if not data.get('registration_address'):
                raise serializers.ValidationError({'registration_address':_("Registration address is required for Legal entity")})

        return data

    class Meta:
        model = DataOceanUser
        fields = (
            'id', 'last_name', 'first_name', 'email',
            'organization', 'position', 'date_of_birth', 'language',
            'person_status', 'iban', 'company_name', 'registration_address',
            'edrpou', 'phone',
        )


class CustomRegisterSerializer(RegisterSerializer):
    username = None
    first_name = serializers.CharField(
        required=True,
        write_only=True,
        max_length=150,
        validators=[name_symbols_validator, two_in_row_validator]
    )
    last_name = serializers.CharField(
        required=True,
        write_only=True,
        max_length=150,
        validators=[name_symbols_validator, two_in_row_validator]
    )

    def get_cleaned_data(self):
        return {
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
            'email': self.validated_data.get('email', ''),
            'password1': self.validated_data.get('password1', ''),
            'password2': self.validated_data.get('password2', ''),
            'phone': self.validated_data.get('phone', ''),
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

        for k, v in cmp_attrs.items():
            if SequenceMatcher(a=data['password1'].lower(), b=data[k].lower()).quick_ratio() >= max_similarity:
                err_msg = _('Your password can’t be too similar to')
                err_msg_result = format_lazy('{err_msg} {v}.', err_msg=err_msg, v=v)
                raise serializers.ValidationError(err_msg_result)
        return data


class CustomLoginSerializer(LoginSerializer):
    username = None
    email = serializers.EmailField(required=True)


class TokenSerializer(serializers.ModelSerializer):
    user = DataOceanUserSerializer()
    project_token = serializers.SerializerMethodField(read_only=True)

    def get_project_token(self, token: Token):
        return token.user.user_projects.get(is_default=True).project.token

    class Meta:
        model = Token
        fields = ('key', 'user', 'project_token')


class CustomPasswordResetSerializer(PasswordResetSerializer):
    password_reset_form_class = CustomPasswordResetForm


class LandingMailSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    subject = serializers.CharField(max_length=150)
    message = serializers.CharField(max_length=500)


class QuestionSerializer(serializers.ModelSerializer):
    text = serializers.CharField(max_length=500, min_length=5, allow_blank=False,
                                 trim_whitespace=True)

    class Meta:
        model = Question
        read_only_fields = ['user', 'answered', 'created_at']
        fields = ['text', ] + read_only_fields

    def create(self, validated_data):
        user = self.context['request'].user
        return Question.objects.create(
            text=validated_data['text'],
            user=user,
        )


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        read_only_fields = ['id', 'message', 'link', 'is_read', 'created_at']
        fields = read_only_fields

