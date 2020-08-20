from rest_framework import serializers

from business_register.models.company_models import (
    BancruptcyReadjustment, CompanyDetail,
    ExchangeDataCompany, TerminationStarted, Company, Founder, HistoricalCompany
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
            'executive_power', 'superior_management', 'managing_paper', 'terminated_info',
            'termination_cancel_info', 'vp_dates')


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
    # retrieving id only for founder that is company
    id_if_company = serializers.SerializerMethodField()

    class Meta:
        model = Founder
        fields = ('name', 'edrpou', 'equity', 'id_if_company')

    def get_id_if_company(self, founder):
        if founder.edrpou:
            company = Company.objects.filter(edrpou=founder.edrpou).first()
            if company:
                return company.id


class TerminationStartedSerializer(serializers.ModelSerializer):
    class Meta:
        model = TerminationStarted
        fields = ('op_date', 'reason', 'sbj_state', 'signer_name', 'creditor_reg_end_date')


class CountFoundedCompaniesSerializer(serializers.ModelSerializer):
    company_type = serializers.StringRelatedField()
    status = serializers.StringRelatedField()
    founder_of_count = serializers.SerializerMethodField()

    def get_founder_of_count(self, company):
        return Founder.objects.filter(edrpou=company.edrpou).count()

    class Meta:
        model = Company
        fields = (
            'id', 'name', 'short_name', 'company_type', 'edrpou', 'status', 'founder_of_count',
            'is_closed',
        )


class CompanyShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ('id', 'name', 'edrpou',)


class CompanyListSerializer(serializers.ModelSerializer):
    founders = FounderSerializer(many=True)
    authorized_capital = serializers.FloatField()
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
        fields = (
            'id', 'name', 'short_name', 'address', 'edrpou', 'founders',
            'authorized_capital', 'parent', 'company_type', 'status', 'is_closed',
            'predecessors', 'authority', 'signers', 'assignees', 'bancruptcy_readjustment',
            'termination_started', 'company_detail', 'kveds', 'bylaw', 'exchange_data'
        )


class CompanyDetailSerializer(serializers.ModelSerializer):
    founders = FounderSerializer(many=True)
    founder_of = serializers.SerializerMethodField()
    relationships_with_peps = serializers.StringRelatedField(many=True)
    authorized_capital = serializers.FloatField()
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

    # getting a list of ids companies that are founded by this company
    def get_founder_of(self, company):
        founder_of = Founder.objects.filter(edrpou=company.edrpou)
        founded_companies = []
        for founder in founder_of:
            founded_companies.append(
                CountFoundedCompaniesSerializer(founder.company).data
            )
        return founded_companies

    class Meta:
        model = Company
        fields = (
            'id', 'name', 'short_name', 'address', 'edrpou', 'founders', 'founder_of',
            'relationships_with_peps', 'authorized_capital', 'parent', 'company_type', 'status',
            'is_closed', 'predecessors', 'authority', 'signers', 'assignees',
            'bancruptcy_readjustment', 'termination_started', 'company_detail', 'kveds', 'bylaw',
            'exchange_data'
        )


class HistoricalCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoricalCompany
        fields = '__all__'
