from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from business_register.filters import PepFilterSet
from business_register.models.pep_models import Pep
from business_register.permissions import PepSchemaToken
from business_register.serializers.company_and_pep_serializers import PepListSerializer, PepDetailSerializer
from data_ocean.views import CachedViewSetMixin, RegisterViewMixin


class PepViewSet(RegisterViewMixin,
                 CachedViewSetMixin,
                 viewsets.ReadOnlyModelViewSet):
    permission_classes = [RegisterViewMixin.permission_classes[0] | PepSchemaToken]
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

    @action(methods=['get'], detail=True, url_path='source-id', serializer_class=PepDetailSerializer)
    @method_decorator(cache_page(settings.CACHE_MIDDLEWARE_SECONDS))
    def retrieve_by_source_id(self, request, pk):
        pep = get_object_or_404(self.get_queryset(), source_id=pk)
        serializer = self.get_serializer(pep)
        return Response(serializer.data)
