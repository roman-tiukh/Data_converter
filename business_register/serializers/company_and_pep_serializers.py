from django.apps import apps
from drf_dynamic_fields import DynamicFieldsMixin
from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers

from business_register.models.company_models import (
    BancruptcyReadjustment, CompanyDetail,
    ExchangeDataCompany, TerminationStarted, Company, Founder, CompanyToKved, Signer, Assignee, CompanyToPredecessor
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
        queryset = getattr(obj, model_related_name).all()
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
    authority = serializers.CharField(max_length=500, help_text=Company._meta.get_field('authority').help_text)
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
    company_type = serializers.StringRelatedField(help_text=Company._meta.get_field('company_type').help_text)
    status = serializers.StringRelatedField(help_text=Company._meta.get_field('status').help_text)
    founder_of_count = serializers.IntegerField(help_text='The number of companies that have a founder '
                                                          'with the same last name as this particular person.')
    id = serializers.IntegerField(help_text='DataOcean\'s internal unique identifier of the object (company).')
    is_closed = serializers.BooleanField(help_text='Boolean type. If its "true" - this company is closed, '
                                                   '"false" - this is an operating company.')
    is_foreign = serializers.BooleanField(help_text='Boolean type. If its "true" - this is a foreign company, '
                                                    '"false" - this is Ukrainian company.')

    class Meta:
        model = Company
        fields = (
            'id', 'name', 'name_en', 'short_name', 'company_type', 'edrpou', 'status', 'founder_of_count',
            'is_closed', 'is_foreign', 'from_antac_only',
        )


class CompanyShortSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(help_text='DataOcean\'s internal unique identifier of the object (company).')

    class Meta:
        model = Company
        fields = ('id', 'name', 'edrpou',)


class CompanyListSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    country = serializers.StringRelatedField(
        help_text=Company._meta.get_field('country').help_text
    )
    founders = FounderSerializer(many=True, help_text=Founder._meta.get_field('company').help_text)
    authorized_capital = serializers.FloatField(
        help_text=Company._meta.get_field('authorized_capital').help_text
    )
    parent = serializers.StringRelatedField(help_text=Company._meta.get_field('parent').help_text)
    predecessors = serializers.StringRelatedField(many=True,
                                                  help_text=CompanyToPredecessor._meta.get_field('company').help_text)
    company_type = serializers.StringRelatedField(help_text=Company._meta.get_field('company_type').help_text)
    status = serializers.StringRelatedField(help_text=Company._meta.get_field('status').help_text)
    authority = serializers.StringRelatedField(help_text=Company._meta.get_field('authority').help_text)
    assignees = serializers.StringRelatedField(many=True, help_text=Assignee._meta.get_field('company').help_text)
    signers = serializers.StringRelatedField(many=True, help_text=Signer._meta.get_field('company').help_text)
    kveds = serializers.StringRelatedField(many=True, help_text=CompanyToKved._meta.get_field('company').help_text)
    bylaw = serializers.StringRelatedField(help_text=Company._meta.get_field('bylaw').help_text)
    bancruptcy_readjustment = BancruptcyReadjustmentSerializer(
        many=True, help_text=BancruptcyReadjustment._meta.get_field('company').help_text)
    company_detail = CompanyDetailInfoSerializer(many=True,
                                                 help_text=CompanyDetail._meta.get_field('company').help_text)
    exchange_data = ExchangeDataCompanySerializer(many=True,
                                                  help_text=ExchangeDataCompany._meta.get_field('company').help_text)
    termination_started = TerminationStartedSerializer(many=True,
                                                       help_text=TerminationStarted._meta.get_field(
                                                           'company').help_text)

    class Meta:
        model = Company
        fields = (
            'id', 'name', 'name_en', 'short_name', 'address', 'address_en', 'country', 'edrpou', 'founders',
            'authorized_capital', 'parent', 'company_type', 'status', 'is_closed',
            'predecessors', 'authority', 'signers', 'assignees', 'bancruptcy_readjustment',
            'termination_started', 'company_detail', 'kveds', 'bylaw', 'exchange_data'
        )


class PepShortSerializer(serializers.ModelSerializer):
    pep_type = serializers.CharField(source='get_pep_type_display', help_text=Pep._meta.get_field('pep_type').help_text)
    id = serializers.IntegerField(help_text='DataOcean\'s internal unique identifier of the object (PEP).')

    class Meta:
        model = Pep
        fields = (
            'id', 'fullname', 'last_job_title', 'last_employer',
            'is_pep', 'pep_type', 'pep_org_ua_link'
        )


class CompanyLinkWithPepSerializer(serializers.ModelSerializer):
    pep = PepShortSerializer()

    class Meta:
        model = CompanyLinkWithPep
        fields = (
            'pep', 'category', 'relationship_type', 'relationship_type_en', 'start_date', 'end_date', 'is_state_company'
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

    country = serializers.StringRelatedField(
        help_text=Company._meta.get_field('country').help_text
    )
    founders = FounderSerializer(many=True, help_text=Founder._meta.get_field('company').help_text)
    authorized_capital = serializers.FloatField(
        help_text=Company._meta.get_field('authorized_capital').help_text
    )
    parent = serializers.StringRelatedField(help_text=Company._meta.get_field('parent').help_text)
    predecessors = serializers.StringRelatedField(many=True,
                                                  help_text=CompanyToPredecessor._meta.get_field('company').help_text)
    company_type = serializers.StringRelatedField(help_text=Company._meta.get_field('company_type').help_text)
    status = serializers.StringRelatedField(help_text=Company._meta.get_field('status').help_text)
    authority = serializers.StringRelatedField(help_text=Company._meta.get_field('authority').help_text)
    assignees = serializers.StringRelatedField(many=True, help_text=Assignee._meta.get_field('company').help_text)
    signers = serializers.StringRelatedField(many=True, help_text=Signer._meta.get_field('company').help_text)
    kveds = serializers.StringRelatedField(many=True, help_text=CompanyToKved._meta.get_field('company').help_text)
    bylaw = serializers.StringRelatedField(help_text=Company._meta.get_field('bylaw').help_text)
    bancruptcy_readjustment = BancruptcyReadjustmentSerializer(
        many=True, help_text=BancruptcyReadjustment._meta.get_field('company').help_text)
    company_detail = CompanyDetailInfoSerializer(many=True,
                                                 help_text=CompanyDetail._meta.get_field('company').help_text)
    exchange_data = ExchangeDataCompanySerializer(many=True,
                                                  help_text=ExchangeDataCompany._meta.get_field('company').help_text)
    termination_started = TerminationStartedSerializer(many=True,
                                                       help_text=TerminationStarted._meta.get_field(
                                                           'company').help_text)

    class Meta:
        model = Company
        fields = (
            'id', 'name', 'name_en', 'short_name', 'address', 'address_en', 'country', 'edrpou', 'founders', 'founder_of',
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
    to_person = PepShortSerializer(help_text=RelatedPersonsLink._meta.get_field('to_person').help_text)
    category_display = serializers.CharField(source='get_category_display',
                                             help_text=RelatedPersonsLink._meta.get_field('category').help_text)

    class Meta:
        model = RelatedPersonsLink
        fields = (
            'to_person',
            'to_person_relationship_type',
            'to_person_relationship_type_en',
            'category',
            'category_display',
            'start_date',
            'confirmation_date',
            'end_date',
        )


class ToRelatedPersonLinkSerializer(serializers.ModelSerializer):
    from_person = PepShortSerializer(help_text=RelatedPersonsLink._meta.get_field('from_person').help_text)
    category_display = serializers.CharField(source='get_category_display',
                                             help_text=RelatedPersonsLink._meta.get_field('category').help_text)

    class Meta:
        model = RelatedPersonsLink
        fields = (
            'from_person',
            'from_person_relationship_type',
            'from_person_relationship_type_en',
            'category',
            'category_display',
            'start_date',
            'confirmation_date',
            'end_date',
        )


class PepLinkWithCompanySerializer(serializers.ModelSerializer):
    company = CompanyShortSerializer(help_text=CompanyLinkWithPep._meta.get_field('company').help_text)
    category_display = serializers.CharField(source='get_category_display',
                                             help_text=CompanyLinkWithPep._meta.get_field('category').help_text)

    class Meta:
        model = CompanyLinkWithPep
        fields = (
            'company', 'category', 'category_display', 'relationship_type',  'relationship_type_en',
            'start_date', 'end_date', 'is_state_company',
        )


class PepDetailLinkWithCompanySerializer(serializers.ModelSerializer):
    company = CountFoundedCompaniesSerializer(help_text=CompanyLinkWithPep._meta.get_field('company').help_text)
    category_display = serializers.CharField(source='get_category_display',
                                             help_text=CompanyLinkWithPep._meta.get_field('category').help_text)

    class Meta:
        model = CompanyLinkWithPep
        fields = (
            'company', 'category', 'category_display', 'relationship_type',  'relationship_type_en',
            'start_date', 'end_date', 'is_state_company',
        )


class PepDetailSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    from_person_links = serializers.SerializerMethodField(
        help_text=RelatedPersonsLink._meta.get_field('from_person').help_text
    )
    to_person_links = serializers.SerializerMethodField(
        help_text=RelatedPersonsLink._meta.get_field('to_person').help_text
    )
    related_companies = serializers.SerializerMethodField(
        help_text='Companies related to personal. Connection established by Anti-Corruption Action Center.'
    )
    check_companies = serializers.SerializerMethodField(
        help_text='Other companies founded by persons with the same fullname as PEP.'
    )
    pep_type = serializers.CharField(source='get_pep_type_display', help_text=Pep._meta.get_field('pep_type').help_text)
    reason_of_termination = serializers.CharField(source='get_reason_of_termination_display',
                                                  help_text=Pep._meta.get_field('reason_of_termination').help_text)
    id = serializers.IntegerField(help_text='DataOcean\'s internal unique identifier of the object (PEP).')

    @swagger_serializer_method(serializer_or_field=FromRelatedPersonLinkSerializer(many=True))
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

    @swagger_serializer_method(serializer_or_field=ToRelatedPersonLinkSerializer(many=True))
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

    @swagger_serializer_method(serializer_or_field=PepDetailLinkWithCompanySerializer(many=True))
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
            queryset = obj.related_companies.select_related(
                'company',
                'company__company_type',
                'company__status'
            )
        return PepDetailLinkWithCompanySerializer(queryset, many=True).data

    @swagger_serializer_method(serializer_or_field=CountFoundedCompaniesSerializer(many=True))
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
            'id', 'first_name', 'last_name', 'middle_name', 'fullname', 'fullname_en',
            'fullname_transcriptions_eng', 'last_job_title', 'last_employer',
            'is_pep', 'pep_type', 'info', 'sanctions', 'criminal_record', 'assets_info',
            'criminal_proceedings', 'wanted', 'date_of_birth', 'place_of_birth', 'place_of_birth_en', 'is_dead',
            'termination_date', 'reason_of_termination', 'to_person_links', 'from_person_links',
            'related_companies', 'check_companies', 'pep_org_ua_link', 'created_at', 'updated_at',
        )


class PepDetailWithoutCheckCompaniesSerializer(PepDetailSerializer):
    check_companies = None

    class Meta(PepDetailSerializer.Meta):
        fields = [f for f in PepDetailSerializer.Meta.fields if f != 'check_companies']


class FromRelatedPersonListSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display',
                                             help_text=RelatedPersonsLink._meta.get_field('category').help_text)

    id = serializers.IntegerField(source='to_person.id',
                                  help_text='DataOcean\'s internal unique identifier of the object (PEP).')
    fullname = serializers.CharField(source='to_person.fullname', help_text=Pep._meta.get_field('fullname').help_text)
    pep_type = serializers.CharField(source='to_person.get_pep_type_display',
                                     help_text=Pep._meta.get_field('pep_type').help_text)

    class Meta:
        model = RelatedPersonsLink
        fields = (
            'id',
            'fullname',
            'pep_type',
            'to_person_relationship_type',
            'to_person_relationship_type_en',
            'category_display',
        )


class ToRelatedPersonListSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display',
                                             help_text=RelatedPersonsLink._meta.get_field('category').help_text)

    id = serializers.IntegerField(source='from_person.id',
                                  help_text='DataOcean\'s internal unique identifier of the object (PEP).')
    fullname = serializers.CharField(source='from_person.fullname', help_text=Pep._meta.get_field('fullname').help_text)
    pep_type = serializers.CharField(source='from_person.get_pep_type_display',
                                     help_text=Pep._meta.get_field('pep_type').help_text)

    class Meta:
        model = RelatedPersonsLink
        fields = (
            'id',
            'fullname',
            'pep_type',
            'from_person_relationship_type',
            'from_person_relationship_type_en',
            'category_display',
        )


class PepListSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    # related_persons = PepShortSerializer(many=True)
    to_person_links = ToRelatedPersonListSerializer(many=True,
                                                    help_text=RelatedPersonsLink._meta.get_field('to_person').help_text)
    from_person_links = FromRelatedPersonListSerializer(
        many=True,
        help_text=RelatedPersonsLink._meta.get_field('from_person').help_text
    )
    related_companies = PepLinkWithCompanySerializer(many=True,
                                                     help_text='Companies related to personal. Connection established '
                                                               'by Anti-Corruption Action Center.')

    pep_type = serializers.CharField(source='get_pep_type_display', help_text=Pep._meta.get_field('pep_type').help_text)
    reason_of_termination = serializers.CharField(source='get_reason_of_termination_display',
                                                  help_text=Pep._meta.get_field('reason_of_termination').help_text)
    id = serializers.IntegerField(help_text='DataOcean\'s internal unique identifier of the object (PEP).')

    class Meta:
        model = Pep
        fields = (
            'id', 'first_name', 'last_name', 'middle_name', 'fullname', 'fullname_en',
            'fullname_transcriptions_eng', 'last_job_title', 'last_employer',
            'is_pep', 'pep_type', 'info', 'sanctions', 'criminal_record', 'assets_info',
            'criminal_proceedings', 'wanted', 'date_of_birth', 'place_of_birth', 'place_of_birth_en', 'is_dead',
            'termination_date', 'reason_of_termination', 'from_person_links', 'to_person_links',
            'related_companies', 'pep_org_ua_link', 'created_at', 'updated_at',
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
