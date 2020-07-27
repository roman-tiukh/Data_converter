from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from business_register.filters import FopFilterSet
from business_register.models.fop_models import Fop
from business_register.serializers.fop_serializers import FopSerializer
from data_ocean.views import CachedViewMixin
from rest_framework.filters import SearchFilter


class FopView(CachedViewMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Fop.objects.select_related(
        'status', 'authority'
    ).prefetch_related(
        'kveds', 'exchange_data'
    ).all()
    serializer_class = FopSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_class = FopFilterSet
    search_fields = ('fullname', 'address')
