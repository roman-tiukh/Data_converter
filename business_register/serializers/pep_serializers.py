from django.db.models import Subquery, OuterRef, Count
from rest_framework import serializers

from business_register.models.company_models import Founder
from business_register.models.pep_models import Pep, PepRelatedPerson, CompanyLinkWithPep
from business_register.serializers.company_serializers import CompanyShortSerializer


class RelatedPersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = PepRelatedPerson
        fields = ('id', 'fullname', 'fullname_eng', 'relationship_type', 'relationship_type_eng',
                  'is_pep', 'start_date', 'confirmation_date', 'end_date')


class CompanyLinkWithPepSerializer(serializers.ModelSerializer):
    company = CompanyShortSerializer()
    # company = serializers.SerializerMethodField()

    class Meta:
        model = CompanyLinkWithPep
        fields = ('id', 'company', 'company_name_eng', 'company_short_name_eng',
                  'relationship_type', 'relationship_type_eng', 'start_date', 'end_date',
                  'is_state_company')


class PepSerializer(serializers.ModelSerializer):
    related_persons = RelatedPersonSerializer(many=True)
    # related_companies = CompanyLinkWithPepSerializer(many=True)
    related_companies = serializers.SerializerMethodField()

    def get_related_companies(self, obj):
        qs = obj.related_companies.select_related('company', 'company__company_type', 'company__status').all()
        return CompanyLinkWithPepSerializer(qs, many=True).data

    class Meta:
        model = Pep
        fields = ('id', 'fullname', 'fullname_eng', 'fullname_transcriptions_eng', 'last_job_title',
                  'last_job_title_eng', 'last_employer', 'last_employer_eng', 'is_pep', 'pep_type',
                  'pep_type_eng', 'url', 'info', 'info_eng', 'sanctions', 'sanctions_eng',
                  'criminal_record', 'criminal_record_eng', 'assets_info', 'assets_info_eng',
                  'criminal_proceedings', 'criminal_proceedings_eng', 'wanted', 'wanted_eng',
                  'date_of_birth', 'place_of_birth', 'place_of_birth_eng', 'is_dead',
                  'termination_date', 'reason_of_termination', 'reason_of_termination_eng',
                  'related_persons', 'related_companies'
                  )
