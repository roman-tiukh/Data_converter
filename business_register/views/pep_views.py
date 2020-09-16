from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import SearchFilter

from business_register.filters import PepFilterSet
from business_register.models.pep_models import Pep
from business_register.serializers.company_and_pep_serializers import PepListSerializer, PepDetailSerializer
from data_ocean.views import CachedViewMixin


class PepViewSet(CachedViewMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Pep.objects.all()
    serializer_class = PepListSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_class = PepFilterSet
    search_fields = (
        'fullname', 'fullname_transcriptions_eng', 'pep_type',
        'last_job_title', 'last_employer',
    )

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PepDetailSerializer
        return super().get_serializer_class()
