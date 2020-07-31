from rest_framework import serializers

from business_register.models.company_models import CompanyType
from business_register.models.kved_models import Kved
from business_register.serializers.kved_serializers import KvedDetailSerializer


class TopKvedSerializer(serializers.ModelSerializer):
    kved = serializers.SerializerMethodField()
    count_companies_with_kved = serializers.IntegerField()

    class Meta:
        model = Kved
        fields = ['kved', 'count_companies_with_kved']

    def get_kved(self, kved):
        kved_queryset = Kved.objects.get(id=kved['kved'])
        return KvedDetailSerializer(kved_queryset).data


class CompanyTypeCountSerializer(serializers.ModelSerializer):
    count_companies = serializers.IntegerField()

    class Meta:
        model = CompanyType
        fields = ['name', 'count_companies']
