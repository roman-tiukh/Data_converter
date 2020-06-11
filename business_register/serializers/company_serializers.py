from rest_framework import serializers

from business_register.models.company_models import(
    Bylaw, CompanyType, Assignee, BancruptcyReadjustment, CompanyDetail,
    CompanyToKved, ExchangeDataCompany, FounderFull, Predecessor,
    CompanyToPredecessor, Signer, TerminationStarted, Company
)


class BylawSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)


class CompanyTypeSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)


class AssigneeSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)


class BancruptcyReadjustmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = BancruptcyReadjustment
        fields = ('op_date', 'reason', 'sbj_state', 'head_name')


class CompanyDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = CompanyDetail
        fields = (
            'founding_document_number',
            'executive_power', 'superior_management', 'authorized_capital',
            'managing_paper', 'terminated_info', 'termination_cancel_info',
            'vp_dates'
        )


class CompanyToKvedSerializer(serializers.ModelSerializer):
    kved = serializers.CharField(max_length=500)

    class Meta:
        model = CompanyToKved
        fields = ('kved', 'primary_kved')


class ExchangeDataCompanySerializer(serializers.ModelSerializer):
    authority = serializers.CharField(max_length=500)
    taxpayer_type = serializers.CharField(max_length=200)

    class Meta:
        model = ExchangeDataCompany
        fields = (
            'authority', 'taxpayer_type', 'start_date', 'start_number',
            'end_date', 'end_number'
        )


class FounderFullSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=1500)


class PredecessorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Predecessor
        fields = ('id', 'name', 'code')


class CompanyToPredecessorSerializer(serializers.Serializer):
    predecessor = serializers.CharField(max_length=100)


class SignerSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=300)


class TerminationStartedSerializer(serializers.ModelSerializer):

    class Meta:
        model = TerminationStarted
        fields = ('op_date', 'reason', 'sbj_state', 'signer_name', 'creditor_reg_end_date')


class CompanySerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=500)
    company_type = serializers.StringRelatedField()
    bylaw = serializers.StringRelatedField()
    status = serializers.CharField(max_length=100)
    authority = serializers.CharField(max_length=500)
    parent = serializers.CharField(max_length=500)
    assignees = AssigneeSerializer(many=True)
    bancruptcy_readjustment = BancruptcyReadjustmentSerializer(many=True)
    company_detail = CompanyDetailSerializer(many=True)
    kveds = CompanyToKvedSerializer(many=True)
    exchange_data = ExchangeDataCompanySerializer(many=True)
    founders = FounderFullSerializer(many=True)
    predecessors = CompanyToPredecessorSerializer(many=True)
    signers = SignerSerializer(many=True)
    termination_started = TerminationStartedSerializer(many=True)

    class Meta:
        model = Company
        fields = '__all__'
