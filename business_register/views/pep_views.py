from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from business_register.filters import PepFilterSet
from business_register.models.pep_models import Pep
from business_register.serializers.pep_serializers import PepSerializer
from data_ocean.views import CachedViewMixin
from rest_framework.filters import SearchFilter


class PepViewSet(CachedViewMixin, viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    queryset = Pep.objects.prefetch_related('related_persons', 'related_companies').all()
    serializer_class = PepSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_class = PepFilterSet
    search_fields = ('fullname', 'fullname_transcriptions_eng')
