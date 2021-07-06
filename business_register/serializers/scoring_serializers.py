from drf_dynamic_fields import DynamicFieldsMixin
from rest_framework import serializers
from business_register.models.declaration_models import PepScoring, Declaration
from business_register.serializers.company_and_pep_serializers import PepShortSerializer


class DeclarationSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_type_display')

    class Meta:
        model = Declaration
        fields = (
            'id',
            'nacp_declaration_id',
            'nacp_declarant_id',
            'year',
            'submission_date',
            'type',
            'type_display',
            'last_job_title',
            'last_employer',
        )


class PepScoringSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    declaration = DeclarationSerializer()
    pep = PepShortSerializer()

    class Meta:
        model = PepScoring
        fields = (
            'id',
            'rule_id',
            'calculation_datetime',
            'score',
            'data',
            'message_uk',
            'message_en',
            'declaration',
            'pep',
            'updated_at',
            'created_at',
        )
