from rest_framework import serializers

from business_register.models.kved_models import Kved
from business_register.serializers.kved_serializers import KvedDetailSerializer


class TopKvedSerializer(serializers.ModelSerializer):
    kved = serializers.SerializerMethodField()
    count_kved = serializers.IntegerField()

    class Meta:
        model = Kved
        fields = ['kved', 'count_kved']

    def get_kved(self, kved):
        kved_info = Kved.objects.get(id=kved['kved'])
        return KvedDetailSerializer(kved_info).data
