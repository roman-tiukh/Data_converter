from data_ocean.models.company_models import Bylaw, CompanyType, Company, Assignee, BancruptcyReadjustment, CompanyDetail, CompanyToKved, ExchangeDataCompany, FounderFull, Predecessor, CompanyToPredecessor, Signer, TerminationStarted
from rest_framework import serializers
from simple_history.models import HistoricalRecords

class BylawSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bylaw
        fields = ('id', 'name')

class CompanyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyType
        fields = ('id', 'name')

class CompanySerializer(serializers.ModelSerializer):
    company_type = serializers.CharField(max_length=100)
    bylaw = serializers.CharField(max_length=300)
    state = serializers.CharField(max_length=100)
    authority = serializers.CharField(max_length=500)
    parent = serializers.CharField(max_length=500)
    assignee = serializers.CharField(max_length=100)
    bancruptcy_readjustment = serializers.CharField(max_length=300)
    company_detail = serializers.CharField(max_length=100)
    company_to_kved = serializers.CharField(max_length=500)
    exchange_data_company = serializers.CharField(max_length=500)
    founder_full = serializers.CharField(max_length=500)
    predecessor = serializers.CharField(max_length=100)
    company_to_predecessor = serializers.CharField(max_length=100)
    signer = serializers.CharField(max_length=300)
    termination_started = serializers.CharField(max_length=300)
    class Meta:
        model = Company
        fields = ('name', 'short_name', 'company_type', 'edrpou', 'address', 'state', 'bylaw', 'registration_date', 'registration_info', 'contact_info', 'authority', 'parent')

class AssigneeSerializer(serializers.ModelSerializer):
    company = serializers.CharField(max_length=500)
    class Meta:
        model = Assignee
        fields = ('id', 'company', 'name')

class BancruptcyReadjustmentSerializer(serializers.ModelSerializer):
    company = serializers.CharField(max_length=500)
    class Meta:
        model = BancruptcyReadjustment
        fields = ('id', 'company', 'op_date', 'reason', 'sbj_state', 'head_name')

class CompanyDetailSerializer(serializers.ModelSerializer):
    company = serializers.CharField(max_length=500)
    class Meta:
        model = CompanyDetail
        fields = ('id',  'company', 'founding_document_number', 'executive_power', 'superior_management', 'authorized_capital', 'head_namemanaging_paper', 'terminated_info', 'termination_cancel_info', 'vp_dates', 'history')

class CompanyToKvedSerializer(serializers.ModelSerializer):
    company = serializers.CharField(max_length=500)
    kved = serializers.CharField(max_length=500)
    class Meta:
        model = CompanyToKved
        fields = ('id', 'company', 'kved', 'primary_kved')

class ExchangeDataCompanySerializer(serializers.ModelSerializer):
    company = serializers.CharField(max_length=500)
    authority = serializers.CharField(max_length=500)
    taxpayer_type = serializers.CharField(max_length=200)
    class Meta:
        model = ExchangeDataCompany
        fields = ('id',  'company', 'authority', 'taxpayer_type', 'start_date', 'start_number', 'end_date', 'end_number')

class FounderFullSerializer(serializers.ModelSerializer):
    company = serializers.CharField(max_length=500)
    class Meta:
        model = FounderFull
        fields = ('id', 'company', 'name')

class PredecessorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Predecessor
        fields = ('id', 'name', 'code')

class CompanyToPredecessorSerializer(serializers.ModelSerializer):
    company = serializers.CharField(max_length=500)
    predecessor = serializers.CharField(max_length=100)
    class Meta:
        model = CompanyToPredecessor
        fields = ('id', 'company', 'predecessor')

class SignerSerializer(serializers.ModelSerializer):
    company = serializers.CharField(max_length=500)
    class Meta:
        model = Signer
        fields = ('id', 'company', 'name')

class TerminationStartedSerializer(serializers.ModelSerializer):
    company = serializers.CharField(max_length=500)
    class Meta:
        model = TerminationStarted
        fields = ('id',  'company', 'op_date', 'reason', 'sbj_state', 'signer_name', 'creditor_reg_end_date')