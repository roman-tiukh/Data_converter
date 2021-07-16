from drf_dynamic_fields import DynamicFieldsMixin
from rest_framework import serializers
from business_register.models.declaration_models import PepScoring, Declaration


class DeclarationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Declaration
        fields = (
            'id',
            'nacp_declaration_id',
            'year',
            'submission_date',
            'nacp_url',
        )


class PepScoringSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    declaration = DeclarationSerializer()
    coefficient = serializers.FloatField()
    relative_score = serializers.FloatField()

    class Meta:
        model = PepScoring
        fields = (
            'id',
            'rule_id',
            'calculation_datetime',
            'score',
            'coefficient',
            'relative_score',
            'data',
            'message_uk',
            'message_en',
            'declaration',
            'updated_at',
            'created_at',
        )
