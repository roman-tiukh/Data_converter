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
    edrpou = serializers.CharField(max_length=260)
    founders = FounderSerializer(many=True)
    founder_of = serializers.SerializerMethodField()
    parent = serializers.StringRelatedField()
    predecessors = serializers.StringRelatedField(many=True)
    company_type = serializers.StringRelatedField()
    status = serializers.StringRelatedField()
    authority = serializers.StringRelatedField()
    assignees = serializers.StringRelatedField(many=True)
    signers = serializers.StringRelatedField(many=True)
    kveds = serializers.StringRelatedField(many=True)
    bylaw = serializers.StringRelatedField()
    bancruptcy_readjustment = BancruptcyReadjustmentSerializer(many=True)
    company_detail = CompanyDetailSerializer(many=True)
    exchange_data = ExchangeDataCompanySerializer(many=True)
    termination_started = TerminationStartedSerializer(many=True)

    class Meta:
        model = Company
        fields = ('name', 'address', 'edrpou', 'founders', 'founder_of', 'parent', 'company_type',
                  'status', 'predecessors', 'authority', 'signers', 'assignees',
                  'bancruptcy_readjustment', 'termination_started', 'company_detail', 'kveds',
                  'bylaw', 'exchange_data')

    # getting a list of ids companies that are founded by this company
    def get_founder_of(self, company):
        founder_of = FounderFull.objects.filter(edrpou=company.edrpou)
        if not founder_of:
            return
        founded_companies = []
        for founder in founder_of:
            founded_companies.append(founder.company.id)
        return founded_companies


class HistoricalCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoricalCompany
        fields = '__all__'
