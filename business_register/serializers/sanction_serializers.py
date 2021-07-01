from rest_framework import serializers
from drf_dynamic_fields import DynamicFieldsMixin
from business_register.models.sanction_models import SanctionType, PersonSanction, CompanySanction, CountrySanction
from location_register.serializers.address_serializers import CountrySerializer


class CountrySanctionSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    country = serializers.StringRelatedField(
        help_text=CountrySanction._meta.get_field('country').help_text
    )
    types_of_sanctions = serializers.StringRelatedField(
        many=True, help_text=SanctionType._meta.get_field('name').help_text
    )

    class Meta:
        model = CountrySanction
        fields = (
            'id', 'country', 'types_of_sanctions', 'start_date', 'end_date',
            'cancellation_condition', 'reasoning', 'reasoning_date',
            'updated_at', 'created_at',
        )


class PersonSanctionSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    countries_of_citizenship = CountrySerializer(
        many=True, help_text=PersonSanction._meta.get_field('countries_of_citizenship').help_text
    )
    types_of_sanctions = serializers.StringRelatedField(
        many=True, help_text=SanctionType._meta.get_field('name').help_text
    )

    class Meta:
        model = PersonSanction
        fields = (
            'id', 'first_name', 'last_name', 'middle_name',
            'full_name', 'full_name_original', 'date_of_birth', 'year_of_birth',
            'place_of_birth', 'address', 'countries_of_citizenship',
            'occupation', 'id_card', 'taxpayer_number', 'additional_info',
            'types_of_sanctions', 'start_date', 'end_date', 'cancellation_condition',
            'reasoning', 'reasoning_date', 'pep',
            'updated_at', 'created_at',
        )


class CompanySanctionSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    country_of_registration = CountrySerializer(
        help_text=CompanySanction._meta.get_field('country_of_registration').help_text
    )
    types_of_sanctions = serializers.StringRelatedField(
        many=True, help_text=SanctionType._meta.get_field('name').help_text
    )

    class Meta:
        model = CompanySanction
        fields = (
            'id', 'name', 'name_original', 'address', 'registration_date',
            'registration_number', 'country_of_registration', 'taxpayer_number',
            'additional_info', 'types_of_sanctions', 'start_date', 'end_date',
            'cancellation_condition', 'reasoning', 'reasoning_date',
            'updated_at', 'created_at',
        )
