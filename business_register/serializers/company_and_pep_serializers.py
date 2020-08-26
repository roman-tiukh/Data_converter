from rest_framework import serializers

from business_register.models.company_models import (
    BancruptcyReadjustment, CompanyDetail,
    ExchangeDataCompany, TerminationStarted, Company, Founder, HistoricalCompany
)
from business_register.models.pep_models import CompanyLinkWithPep, Pep, PepRelatedPerson


class BancruptcyReadjustmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BancruptcyReadjustment
        fields = ('op_date', 'reason', 'sbj_state', 'head_name')


class CompanyDetailInfoSerializer(serializers.ModelSerializer):
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
    class Meta:
        model = Founder
        fields = ('name', 'edrpou', 'equity', 'id_if_company')


class TerminationStartedSerializer(serializers.ModelSerializer):
    class Meta:
        model = TerminationStarted
        fields = ('op_date', 'reason', 'sbj_state', 'signer_name', 'creditor_reg_end_date')


class CountFoundedCompaniesSerializer(serializers.ModelSerializer):
    company_type = serializers.StringRelatedField()
    status = serializers.StringRelatedField()

    class Meta:
        model = Company
        fields = (
            'id', 'name', 'short_name', 'company_type', 'edrpou',
            'status', 'founder_of_count', 'is_closed', 'from_antac_only',
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
    company_detail = CompanyDetailInfoSerializer(many=True)
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


class PepShortSerializer(serializers.ModelSerializer):
    # check_companies = CountFoundedCompaniesSerializer(many=True)

    class Meta:
        model = Pep
        fields = (
            'id', 'fullname', 'last_job_title', 'last_employer',
            'is_pep', 'pep_type', 'url',
            # 'related_persons', 'related_companies', 'check_companies',
        )


class CompanyLinkWithPepSerializer(serializers.ModelSerializer):
    pep = PepShortSerializer()

    class Meta:
        model = CompanyLinkWithPep
        fields = (
            'pep', 'company_name_eng', 'company_short_name_eng', 'relationship_type',
            'relationship_type_eng', 'start_date', 'end_date', 'is_state_company'
        )


class CompanyDetailSerializer(serializers.ModelSerializer):
    founders = FounderSerializer(many=True)
    founder_of = CountFoundedCompaniesSerializer(many=True)
    relationships_with_peps = CompanyLinkWithPepSerializer(many=True)
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
    company_detail = CompanyDetailInfoSerializer(many=True)
    exchange_data = ExchangeDataCompanySerializer(many=True)
    termination_started = TerminationStartedSerializer(many=True)

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


class RelatedPersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = PepRelatedPerson
        fields = (
            'id', 'fullname', 'fullname_eng', 'relationship_type', 'relationship_type_eng',
            'is_pep', 'start_date', 'confirmation_date', 'end_date'
        )


class PepLinkWithCompanySerializer(serializers.ModelSerializer):
    company = CompanyShortSerializer()

    class Meta:
        model = CompanyLinkWithPep
        fields = (
            'company', 'company_name_eng', 'company_short_name_eng',
            'relationship_type', 'relationship_type_eng', 'start_date', 'end_date',
            'is_state_company',
        )


class PepDetailLinkWithCompanySerializer(serializers.ModelSerializer):
    company = CountFoundedCompaniesSerializer()

    class Meta:
        model = CompanyLinkWithPep
        fields = (
            'company', 'company_name_eng', 'company_short_name_eng', 'relationship_type',
            'relationship_type_eng', 'start_date', 'end_date', 'is_state_company',
        )


class PepDetailSerializer(serializers.ModelSerializer):
    related_persons = RelatedPersonSerializer(many=True)
    related_companies = serializers.SerializerMethodField()
    # other companies founded by persons with the same fullname as pep
    check_companies = CountFoundedCompaniesSerializer(many=True)

    def get_related_companies(self, obj):
        queryset = obj.related_companies.select_related('company', 'company__company_type', 'company__status').all()
        return PepDetailLinkWithCompanySerializer(queryset, many=True).data

    class Meta:
        model = Pep
        fields = (
            'id', 'fullname', 'fullname_eng', 'fullname_transcriptions_eng', 'last_job_title',
            'last_job_title_eng', 'last_employer', 'last_employer_eng', 'is_pep', 'pep_type',
            'pep_type_eng', 'url', 'info', 'info_eng', 'sanctions', 'sanctions_eng',
            'criminal_record', 'criminal_record_eng', 'assets_info', 'assets_info_eng',
            'criminal_proceedings', 'criminal_proceedings_eng', 'wanted', 'wanted_eng',
            'date_of_birth', 'place_of_birth', 'place_of_birth_eng', 'is_dead',
            'termination_date', 'reason_of_termination', 'reason_of_termination_eng',
            'related_persons', 'related_companies', 'check_companies', 'created_at', 'updated_at',
        )


class PepListSerializer(serializers.ModelSerializer):
    related_persons = RelatedPersonSerializer(many=True)
    related_companies = PepLinkWithCompanySerializer(many=True)

    class Meta:
        model = Pep
        fields = (
            'id', 'fullname', 'fullname_eng', 'fullname_transcriptions_eng', 'last_job_title',
            'last_job_title_eng', 'last_employer', 'last_employer_eng', 'is_pep', 'pep_type',
            'pep_type_eng', 'url', 'info', 'info_eng', 'sanctions', 'sanctions_eng',
            'criminal_record', 'criminal_record_eng', 'assets_info', 'assets_info_eng',
            'criminal_proceedings', 'criminal_proceedings_eng', 'wanted', 'wanted_eng',
            'date_of_birth', 'place_of_birth', 'place_of_birth_eng', 'is_dead',
            'termination_date', 'reason_of_termination', 'reason_of_termination_eng',
            'related_persons', 'related_companies', 'created_at', 'updated_at',
        )
