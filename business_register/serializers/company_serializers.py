from rest_framework import serializers

from business_register.models.company_models import (
    BancruptcyReadjustment, CompanyDetail,
    ExchangeDataCompany, TerminationStarted, Company, FounderFull, HistoricalCompany
)


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


class ExchangeDataCompanySerializer(serializers.ModelSerializer):
    authority = serializers.CharField(max_length=500)
    taxpayer_type = serializers.CharField(max_length=200)

    class Meta:
        model = ExchangeDataCompany
        fields = (
            'authority', 'taxpayer_type', 'start_date', 'start_number',
            'end_date', 'end_number'
        )


class FounderSerializer(serializers.ModelSerializer):
    # retreiving id only for founder that is company
    id_if_company = serializers.SerializerMethodField()
    class Meta:
        model = FounderFull
        fields = ('name', 'edrpou', 'equity', 'id_if_company')

    def get_id_if_company(self, founderfull):
        if founderfull.edrpou:
            company = Company.objects.filter(edrpou=founderfull.edrpou).first()
            if company:
                return company.id

class TerminationStartedSerializer(serializers.ModelSerializer):
    class Meta:
        model = TerminationStarted
        fields = ('op_date', 'reason', 'sbj_state', 'signer_name', 'creditor_reg_end_date')


class CompanySerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=500)
    short_name = serializers.CharField(max_length=500)
    company_type = serializers.StringRelatedField()
    bylaw = serializers.StringRelatedField()
    status = serializers.StringRelatedField()
    authority = serializers.StringRelatedField()
    parent = serializers.StringRelatedField()
    assignees = serializers.StringRelatedField(many=True)
    bancruptcy_readjustment = BancruptcyReadjustmentSerializer(many=True)
    company_detail = CompanyDetailSerializer(many=True)
    kveds = serializers.StringRelatedField(many=True)
    exchange_data = ExchangeDataCompanySerializer(many=True)
    founders = FounderSerializer(many=True)
    predecessors = serializers.StringRelatedField(many=True)
    signers = serializers.StringRelatedField(many=True)
    termination_started = TerminationStartedSerializer(many=True)

    class Meta:
        model = Company
        fields = '__all__'


class HistoricalCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoricalCompany
        fields = '__all__'
