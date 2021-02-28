from django.apps import apps
from drf_dynamic_fields import DynamicFieldsMixin
from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _

from business_register.models.company_models import (
    BancruptcyReadjustment, CompanyDetail,
    ExchangeDataCompany, TerminationStarted, Company, Founder
)
from business_register.models.pep_models import CompanyLinkWithPep, Pep, RelatedPersonsLink

HistoricalAssignee = apps.get_model('business_register', 'HistoricalAssignee')
HistoricalBancruptcyReadjustment = apps.get_model('business_register', 'HistoricalBancruptcyReadjustment')
HistoricalCompany = apps.get_model('business_register', 'HistoricalCompany')
HistoricalCompanyDetail = apps.get_model('business_register', 'HistoricalCompanyDetail')
HistoricalCompanyToKved = apps.get_model('business_register', 'HistoricalCompanyToKved')
HistoricalCompanyToPredecessor = apps.get_model('business_register', 'HistoricalCompanyToPredecessor')
HistoricalExchangeDataCompany = apps.get_model('business_register', 'HistoricalExchangeDataCompany')
HistoricalFounder = apps.get_model('business_register', 'HistoricalFounder')
HistoricalSigner = apps.get_model('business_register', 'HistoricalSigner')
HistoricalTerminationStarted = apps.get_model('business_register', 'HistoricalTerminationStarted')


def filter_with_parameter(obj, parameter, used_categories, model_related_name, serializer):
    if parameter == 'none':
        return []
    if parameter:
        categories = parameter.split(',')
        for category in categories:
            if category not in used_categories:
                categories.remove(category)
        queryset = getattr(obj, model_related_name).filter(
            category__in=categories
        )
    else:
        queryset = getattr(obj, model_related_name).filter(
            category__in=used_categories
        )
    return serializer(queryset, many=True).data


def filter_property(obj, parameter, model_related_name, serializer):
    if parameter == 'none':
        return []
    else:
        result = getattr(obj, model_related_name)
        return serializer(result, many=True).data


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
    authority = serializers.CharField(max_length=500, help_text=_('Authority'))
    taxpayer_type = serializers.CharField(max_length=200, help_text=_('Taxpayer type'))

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
    company_type = serializers.StringRelatedField(help_text=_('Type of company'))
    status = serializers.StringRelatedField(help_text=_('Status'))

    class Meta:
        model = Company
        fields = (
            'id', 'name', 'short_name', 'company_type', 'edrpou', 'status', 'founder_of_count',
            'is_closed', 'is_foreign', 'from_antac_only',
        )


class CompanyShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ('id', 'name', 'edrpou',)


class CompanyListSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    country = serializers.StringRelatedField(help_text=_('Country of origin'))
    founders = FounderSerializer(many=True, help_text=_('Founders'))
    authorized_capital = serializers.FloatField(help_text=_('Authorized capital'))
    parent = serializers.StringRelatedField(help_text=_('Parent company'))
    predecessors = serializers.StringRelatedField(many=True, help_text=_('Predecessors'))
    company_type = serializers.StringRelatedField(help_text=_('Type of company'))
    status = serializers.StringRelatedField(help_text=_('Status'))
    authority = serializers.StringRelatedField(help_text=_('Authority'))
    assignees = serializers.StringRelatedField(many=True, help_text=_('Assignees'))
    signers = serializers.StringRelatedField(many=True, help_text=_('Signers'))
    kveds = serializers.StringRelatedField(many=True, help_text=_("NACE's"))
    bylaw = serializers.StringRelatedField(help_text=_('By law'))
    bancruptcy_readjustment = BancruptcyReadjustmentSerializer(many=True, help_text=_('Bankruptcy readjustment'))
    company_detail = CompanyDetailInfoSerializer(many=True, help_text=_('Company detail'))
    exchange_data = ExchangeDataCompanySerializer(many=True, help_text=_('Data exchange'))
    termination_started = TerminationStartedSerializer(many=True,  help_text=_('When termination started'))

    class Meta:
        model = Company
        fields = (
            'id', 'name', 'short_name', 'address', 'country', 'edrpou', 'founders',
            'authorized_capital', 'parent', 'company_type', 'status', 'is_closed',
            'predecessors', 'authority', 'signers', 'assignees', 'bancruptcy_readjustment',
            'termination_started', 'company_detail', 'kveds', 'bylaw', 'exchange_data'
        )


class PepShortSerializer(serializers.ModelSerializer):
    pep_type = serializers.CharField(source='get_pep_type_display', help_text=_('Type of PEP'))

    class Meta:
        model = Pep
        fields = (
            'id', 'fullname', 'last_job_title', 'last_employer',
            'is_pep', 'pep_type'
        )


class CompanyLinkWithPepSerializer(serializers.ModelSerializer):
    pep = PepShortSerializer(help_text=_('PEP'))

    class Meta:
        model = CompanyLinkWithPep
        fields = (
            'pep', 'category', 'relationship_type', 'start_date', 'end_date', 'is_state_company'
        )


class CompanyDetailSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    relationships_with_peps = serializers.SerializerMethodField(help_text=_("Reletionships with PEP's"))
    founder_of = serializers.SerializerMethodField(help_text=_('Is founder'))

    def get_relationships_with_peps(self, obj):
        return filter_with_parameter(
            obj=obj,
            parameter=self.context['request'].query_params.get('peps_relations'),
            used_categories=[
                CompanyLinkWithPep.OWNER,
                CompanyLinkWithPep.MANAGER
            ],
            model_related_name='relationships_with_peps',
            serializer=CompanyLinkWithPepSerializer
        )

    def get_founder_of(self, obj):
        return filter_property(
            obj=obj,
            parameter=self.context['request'].query_params.get('show_founder_of'),
            model_related_name='founder_of',
            serializer=CountFoundedCompaniesSerializer
        )

    country = serializers.StringRelatedField(help_text=_('Country of origin'))
    founders = FounderSerializer(many=True, help_text=_('Founders'))
    authorized_capital = serializers.FloatField(help_text=_('Authorized capital'))
    parent = serializers.StringRelatedField(help_text=_('Parent company'))
    predecessors = serializers.StringRelatedField(many=True, help_text=_('Predecessors'))
    company_type = serializers.StringRelatedField(help_text=_('Type of company'))
    status = serializers.StringRelatedField(help_text=_('Status'))
    authority = serializers.StringRelatedField(help_text=_('Authority'))
    assignees = serializers.StringRelatedField(many=True, help_text=_('Assignees'))
    signers = serializers.StringRelatedField(many=True, help_text=_('Signers'))
    kveds = serializers.StringRelatedField(many=True, help_text=_("NACE's"))
    bylaw = serializers.StringRelatedField(help_text=_('By law'))
    bancruptcy_readjustment = BancruptcyReadjustmentSerializer(many=True, help_text=_('Bankruptcy readjustment'))
    company_detail = CompanyDetailInfoSerializer(many=True, help_text=_('Company detail'))
    exchange_data = ExchangeDataCompanySerializer(many=True, help_text=_('Data exchange'))
    termination_started = TerminationStartedSerializer(many=True, help_text=_('When termination started'))

    class Meta:
        model = Company
        fields = (
            'id', 'name', 'short_name', 'address', 'country', 'edrpou', 'founders', 'founder_of',
            'relationships_with_peps', 'authorized_capital', 'parent', 'company_type', 'status',
            'is_closed', 'predecessors', 'authority', 'signers', 'assignees',
            'bancruptcy_readjustment', 'termination_started', 'company_detail', 'kveds', 'bylaw',
            'exchange_data'
        )


class HistoricalAssigneeSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoricalAssignee
        fields = '__all__'


class HistoricalBancruptcyReadjustmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoricalBancruptcyReadjustment
        fields = '__all__'


class HistoricalCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoricalCompany
        fields = '__all__'


class HistoricalCompanyDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoricalCompanyDetail
        fields = '__all__'


class HistoricalCompanyToKvedSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoricalCompanyToKved
        fields = '__all__'


class HistoricalCompanyToPredecessorSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoricalCompanyToPredecessor
        fields = '__all__'


class HistoricalExchangeDataCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoricalExchangeDataCompany
        fields = '__all__'


class HistoricalFounderSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoricalFounder
        fields = '__all__'


class HistoricalSignerSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoricalSigner
        fields = '__all__'


class HistoricalTerminationStartedSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoricalTerminationStarted
        fields = '__all__'


class FromRelatedPersonLinkSerializer(serializers.ModelSerializer):
    to_person = PepShortSerializer(help_text=_('To person'))
    category_display = serializers.CharField(source='get_category_display', help_text=_('Category'))

    class Meta:
        model = RelatedPersonsLink
        fields = (
            'to_person',
            'to_person_relationship_type',
            'category',
            'category_display',
            'start_date',
            'confirmation_date',
            'end_date',
        )


class ToRelatedPersonLinkSerializer(serializers.ModelSerializer):
    from_person = PepShortSerializer(help_text=_('From person'))
    category_display = serializers.CharField(source='get_category_display', help_text=_('Category'))

    class Meta:
        model = RelatedPersonsLink
        fields = (
            'from_person',
            'from_person_relationship_type',
            'category',
            'category_display',
            'start_date',
            'confirmation_date',
            'end_date',
        )


class PepLinkWithCompanySerializer(serializers.ModelSerializer):
    company = CompanyShortSerializer(help_text=_('Company name'))
    category_display = serializers.CharField(source='get_category_display', help_text=_('Category'))

    class Meta:
        model = CompanyLinkWithPep
        fields = (
            'company', 'category', 'category_display', 'relationship_type',
            'start_date', 'end_date', 'is_state_company',
        )


class PepDetailLinkWithCompanySerializer(serializers.ModelSerializer):
    company = CountFoundedCompaniesSerializer(help_text=_('Company name'))
    category_display = serializers.CharField(source='get_category_display', help_text=_('Category'))

    class Meta:
        model = CompanyLinkWithPep
        fields = (
            'company', 'category', 'category_display', 'relationship_type',
            'start_date', 'end_date', 'is_state_company',
        )


class PepDetailSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    from_person_links = serializers.SerializerMethodField(help_text=_('From person'))
    to_person_links = serializers.SerializerMethodField(help_text=_('To person'))
    related_companies = serializers.SerializerMethodField(help_text=_('Related companies'))
    # other companies founded by persons with the same fullname as pep
    check_companies = serializers.SerializerMethodField(help_text=_('Check companies'))
    pep_type = serializers.CharField(source='get_pep_type_display', help_text=_('PEP type'))
    reason_of_termination = serializers.CharField(source='get_reason_of_termination_display',
                                                  help_text=_('Reason of termination'))

    def get_from_person_links(self, obj):
        return filter_with_parameter(
            obj=obj,
            parameter=self.context['request'].query_params.get('pep_relations'),
            used_categories=[
                RelatedPersonsLink.FAMILY,
                RelatedPersonsLink.BUSINESS,
                RelatedPersonsLink.PERSONAL
            ],
            model_related_name='from_person_links',
            serializer=FromRelatedPersonLinkSerializer)

    def get_to_person_links(self, obj):
        return filter_with_parameter(
            obj=obj,
            parameter=self.context['request'].query_params.get('pep_relations'),
            used_categories=[
                RelatedPersonsLink.FAMILY,
                RelatedPersonsLink.BUSINESS,
                RelatedPersonsLink.PERSONAL
            ],
            model_related_name='to_person_links',
            serializer=ToRelatedPersonLinkSerializer
        )

    def get_related_companies(self, obj):
        parameter = self.context['request'].query_params.get('company_relations')
        if parameter == 'none':
            return []
        used_categories = [
            CompanyLinkWithPep.OWNER,
            CompanyLinkWithPep.MANAGER
        ]
        if parameter:
            categories = parameter.split(',')
            for category in categories:
                if category not in used_categories:
                    categories.remove(category)
            queryset = obj.related_companies.filter(
                category__in=categories
            ).select_related(
                'company',
                'company__company_type',
                'company__status'
            )
        else:
            queryset = obj.related_companies.filter(
                category__in=used_categories
            ).select_related(
                'company',
                'company__company_type',
                'company__status'
            )
        return PepDetailLinkWithCompanySerializer(queryset, many=True).data

    def get_check_companies(self, obj):
        return filter_property(
            obj=obj,
            parameter=self.context['request'].query_params.get('show_check_companies'),
            model_related_name='check_companies',
            serializer=CountFoundedCompaniesSerializer
        )

    class Meta:
        model = Pep
        fields = (
            'id', 'fullname', 'fullname_transcriptions_eng', 'last_job_title', 'last_employer',
            'is_pep', 'pep_type', 'info',
            'sanctions', 'criminal_record', 'assets_info', 'criminal_proceedings', 'wanted',
            'date_of_birth', 'place_of_birth', 'is_dead',
            'termination_date', 'reason_of_termination',
            'to_person_links', 'from_person_links', 'related_companies', 'check_companies', 'created_at',
            'updated_at'
        )


class PepListSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    related_persons = PepShortSerializer(many=True, help_text=_('Related person'))
    related_companies = PepLinkWithCompanySerializer(many=True, help_text=_('Related companies'))
    pep_type = serializers.CharField(source='get_pep_type_display', help_text=_('PEP type'))
    reason_of_termination = serializers.CharField(source='get_reason_of_termination_display',
                                                  help_text=_('Reason of termination'))

    class Meta:
        model = Pep
        fields = (
            'id', 'fullname', 'fullname_transcriptions_eng', 'last_job_title', 'last_employer',
            'is_pep', 'pep_type', 'info',
            'sanctions', 'criminal_record', 'assets_info', 'criminal_proceedings', 'wanted',
            'date_of_birth', 'place_of_birth', 'is_dead',
            'termination_date', 'reason_of_termination',
            'related_persons', 'related_companies', 'created_at', 'updated_at',
        )
