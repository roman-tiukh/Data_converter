from rest_framework import serializers
from drf_dynamic_fields import DynamicFieldsMixin
from business_register.models.sanction_models import SanctionType, PersonSanction, CompanySanction, CountrySanction


class SanctionTypeSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = SanctionType
        fields = ('name', 'law')


class CountrySanctionSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    country = serializers.StringRelatedField(
        help_text=CountrySanction._meta.get_field('country').help_text
    )
    types_of_sanctions = SanctionTypeSerializer(
        many=True, help_text=SanctionType._meta.get_field('name').help_text
    )

    class Meta:
        model = CountrySanction
        fields = (
            'country',
            'types_of_sanctions', 'start_date', 'end_date', 'cancellation_condition', 'reasoning'
        )


class PersonSanctionSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    countries_of_citizenship = serializers.StringRelatedField(
        many=True, help_text=PersonSanction._meta.get_field('countries_of_citizenship').help_text
    )
    types_of_sanctions = SanctionTypeSerializer(
        many=True, help_text=SanctionType._meta.get_field('name').help_text
    )

    class Meta:
        model = PersonSanction
        fields = (
            'is_foreign', 'pep',
            'full_name', 'full_name_original_transcription',
            'date_of_birth', 'place_of_birth', 'address', 'countries_of_citizenship',
            'occupation', 'id_card', 'taxpayer_number',
            'types_of_sanctions', 'start_date', 'end_date', 'cancellation_condition', 'reasoning'
        )


class CompanySanctionSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    country_of_registration = serializers.StringRelatedField(
        help_text=CompanySanction._meta.get_field('country_of_registration').help_text
    )
    types_of_sanctions = SanctionTypeSerializer(
        many=True, help_text=SanctionType._meta.get_field('name').help_text
    )

    class Meta:
        model = CompanySanction
        fields = (
            'is_foreign', 'company',
            'name', 'name_original_transcription',
            'address', 'registration_date', 'registration_number', 'country_of_registration',
            'taxpayer_number',
            'types_of_sanctions', 'start_date', 'end_date', 'cancellation_condition', 'reasoning'
        )
