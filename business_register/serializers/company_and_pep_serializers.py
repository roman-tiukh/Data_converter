from django.apps import apps
from drf_dynamic_fields import DynamicFieldsMixin
from rest_framework import serializers

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
            'id', 'name', 'short_name', 'company_type', 'edrpou', 'status', 'founder_of_count',
            'is_closed', 'is_foreign', 'from_antac_only',
        )


class CompanyShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ('id', 'name', 'edrpou',)


class CompanyListSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    country = serializers.StringRelatedField()
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
            'id', 'name', 'short_name', 'address', 'country', 'edrpou', 'founders',
            'authorized_capital', 'parent', 'company_type', 'status', 'is_closed',
            'predecessors', 'authority', 'signers', 'assignees', 'bancruptcy_readjustment',
            'termination_started', 'company_detail', 'kveds', 'bylaw', 'exchange_data'
        )


class PepShortSerializer(serializers.ModelSerializer):
    pep_type = serializers.CharField(source='get_pep_type_display',
                                     help_text='Type of politically exposed person. Can be national politically exposed '
                                               'person, foreign politically exposed person,  politically exposed person,'
                                               ' having political functions in international organization, associated '
                                               'person or family member.')

    class Meta:
        model = Pep
        fields = (
            'id', 'fullname', 'last_job_title', 'last_employer',
            'is_pep', 'pep_type'
        )


class CompanyLinkWithPepSerializer(serializers.ModelSerializer):
    pep = PepShortSerializer()

    class Meta:
        model = CompanyLinkWithPep
        fields = (
            'pep', 'category', 'relationship_type', 'start_date', 'end_date', 'is_state_company'
        )


class CompanyDetailSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    relationships_with_peps = serializers.SerializerMethodField()
    founder_of = serializers.SerializerMethodField()

    def get_relationships_with_peps(self, obj):
        return filter_with_parameter(
            obj=obj,
            parameter=self.context['request'].query_params.get('peps_relations'),
            used_categories=[
                CompanyLinkWithPep.OWNER,
                CompanyLinkWithPep.MANAGER
            ],
            model_related_name='relationships_with_peps',
            serializer=CompanyLinkWithPepSerializer,
        )

    def get_founder_of(self, obj):
        return filter_property(
            obj=obj,
            parameter=self.context['request'].query_params.get('show_founder_of'),
            model_related_name='founder_of',
            serializer=CountFoundedCompaniesSerializer
        )

    country = serializers.StringRelatedField()
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
    to_person = PepShortSerializer()
    category_display = serializers.CharField(source='get_category_display')

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
    from_person = PepShortSerializer()
    category_display = serializers.CharField(source='get_category_display')

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
    company = CompanyShortSerializer()
    category_display = serializers.CharField(source='get_category_display')

    class Meta:
        model = CompanyLinkWithPep
        fields = (
            'company', 'category', 'category_display', 'relationship_type',
            'start_date', 'end_date', 'is_state_company',
        )


class PepDetailLinkWithCompanySerializer(serializers.ModelSerializer):
    company = CountFoundedCompaniesSerializer()
    category_display = serializers.CharField(source='get_category_display')

    class Meta:
        model = CompanyLinkWithPep
        fields = (
            'company', 'category', 'category_display', 'relationship_type',
            'start_date', 'end_date', 'is_state_company',
        )


class PepDetailSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    from_person_links = serializers.SerializerMethodField()
    to_person_links = serializers.SerializerMethodField()
    related_companies = serializers.SerializerMethodField()
    # other companies founded by persons with the same fullname as pep
    check_companies = serializers.SerializerMethodField()
    pep_type = serializers.CharField(source='get_pep_type_display',
                                     help_text='Type of politically exposed person. Can be national politically exposed '
                                               'person, foreign politically exposed person,  politically exposed person,'
                                               ' having political functions in international organization, associated '
                                               'person or family member.')
    reason_of_termination = serializers.CharField(source='get_reason_of_termination_display',
                                                  help_text='Reason for terminating PEP status.')

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


class FromRelatedPersonListSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display')

    id = serializers.IntegerField(source='to_person.id')
    fullname = serializers.CharField(source='to_person.fullname')
    pep_type = serializers.CharField(source='to_person.get_pep_type_display')

    class Meta:
        model = RelatedPersonsLink
        fields = (
            'id',
            'fullname',
            'pep_type',
            'to_person_relationship_type',
            'category_display',
        )


class ToRelatedPersonListSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display')

    id = serializers.IntegerField(source='from_person.id')
    fullname = serializers.CharField(source='from_person.fullname')
    pep_type = serializers.CharField(source='from_person.get_pep_type_display')

    class Meta:
        model = RelatedPersonsLink
        fields = (
            'id',
            'fullname',
            'pep_type',
            'from_person_relationship_type',
            'category_display',
        )


class PepListSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    # related_persons = PepShortSerializer(many=True)
    to_person_links = ToRelatedPersonListSerializer(many=True)
    from_person_links = FromRelatedPersonListSerializer(many=True)
    related_companies = PepLinkWithCompanySerializer(many=True)

    pep_type = serializers.CharField(source='get_pep_type_display',
                                     help_text='Type of politically exposed person. Can be national politically exposed person, '
                                               'foreign politically exposed person, politically exposed person, having '
                                               'political functions in international organization, associated person or family member.')
    reason_of_termination = serializers.CharField(source='get_reason_of_termination_display',
                                                  help_text='Reason for terminating PEP status.')

    class Meta:
        model = Pep
        fields = (
            'id', 'fullname', 'fullname_transcriptions_eng', 'last_job_title', 'last_employer',
            'is_pep', 'pep_type', 'info', 'sanctions', 'criminal_record', 'assets_info',
            'criminal_proceedings', 'wanted', 'date_of_birth', 'place_of_birth', 'is_dead',
            'termination_date', 'reason_of_termination', 'from_person_links', 'to_person_links',
            'related_companies', 'created_at', 'updated_at',
        )


# class PepListFreemiumSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
#     pep_type = serializers.CharField(
#     source='get_pep_type_display',
#     help_text='Type of politically exposed person. Can be national politically exposed person, '
#               'foreign politically exposed person, politically exposed person, having '
#               'political functions in international organization, associated person or family member.'
#     )
#
#     class Meta:
#         model = Pep
#         fields = (
#             'id',
#             'fullname',
#             'fullname_transcriptions_eng'
#             'is_pep',
#             'pep_type',
#             'date_of_birth',
#             'created_at',
#             'updated_at',
#         )
