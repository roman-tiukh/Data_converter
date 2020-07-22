from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from business_register.filters import KvedFilterSet
from business_register.models.kved_models import Kved
from business_register.serializers.kved_serializers import KvedDetailSerializer


class KvedView(viewsets.ReadOnlyModelViewSet):
    queryset = Kved.objects.exclude(is_valid=False)
    serializer_class = KvedDetailSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_class = KvedFilterSet
    search_fields = ('code', 'name')
