from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from business_register.filters import FopFilterSet
from business_register.models.fop_models import Fop
from business_register.serializers.fop_serializers import FopSerializer
from data_ocean.views import CachedViewSetMixin, RegisterViewMixin
from rest_framework.filters import SearchFilter


class FopViewSet(RegisterViewMixin,
                 CachedViewSetMixin,
                 viewsets.ReadOnlyModelViewSet):
    queryset = Fop.objects.select_related(
        'status', 'authority'
    ).prefetch_related(
        'kveds', 'exchange_data'
    ).all()
    filter_backends = (DjangoFilterBackend, SearchFilter)
    serializer_class = FopSerializer
    filterset_class = FopFilterSet
    search_fields = ('fullname', 'address', 'status__name')
