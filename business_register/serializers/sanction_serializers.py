from rest_framework import serializers
from business_register.models.sanction_models import SanctionType, Sanction


class SanctionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SanctionType
        fields = ('name', 'law')


class SanctionSerializer(serializers.ModelSerializer):
    types_of_sanctions = SanctionTypeSerializer(
        many=True, help_text=SanctionType._meta.get_field('name').help_text
    )
    country = serializers.StringRelatedField(
        help_text=Sanction._meta.get_field('country').help_text
    )

    class Meta:
        model = Sanction
        fields = (
            'object_type', 'is_foreign', 'object_name', 'object_origin_name', 'country',
            'date_of_birth', 'place_of_birth', 'address',
            'registration_date', 'registration_number', 'taxpayer_number',
            'position', 'id_card',
            'types_of_sanctions', 'imposed_by', 'start_date', 'end_date', 'reasoning'
        )
