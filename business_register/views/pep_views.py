from datetime import datetime, timedelta, timezone
import pytz
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from business_register.filters import PepFilterSet, PepExportFilterSet
from business_register.models.pep_models import Pep
from business_register.permissions import PepSchemaToken
from business_register.serializers.company_and_pep_serializers import PepListSerializer, PepDetailSerializer
from data_converter.filter import DODjangoFilterBackend
from data_ocean.views import CachedViewSetMixin, RegisterViewMixin


@method_decorator(name='retrieve', decorator=swagger_auto_schema(tags=['pep']))
@method_decorator(name='list', decorator=swagger_auto_schema(tags=['pep']))
@method_decorator(name='retrieve_by_source_id', decorator=swagger_auto_schema(auto_schema=None))
@method_decorator(name='export_to_xlsx', decorator=swagger_auto_schema(auto_schema=None))
class PepViewSet(RegisterViewMixin,
                 CachedViewSetMixin,
                 viewsets.ReadOnlyModelViewSet):
    permission_classes = [RegisterViewMixin.permission_classes[0] | PepSchemaToken]
    queryset = Pep.objects.all()
    serializer_class = PepListSerializer
    filter_backends = (DODjangoFilterBackend, SearchFilter)
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

    @action(detail=False, url_path='xlsx')
    def export_to_xlsx(self, request):
        export_dict = {
            'ID': ['pk', 7],
            'Full Name': ['fullname', 30],
            'Full Name (english transcription)': ['fullname_transcriptions_eng', 36],
            'Status': ['is_pep', 10],
            'PEP Type': ['pep_type', 10],
            'Date of Birth': ['date_of_birth', 19],
            'Created Date': ['created_at', 19],
            'Updated Date': ['updated_at', 19],
            'Last Job Title': ['last_job_title', 20],
            'Last Employer': ['last_employer', 20]
        }
        from business_register.tasks import export_to_s3
        export_to_s3.delay(request.GET, export_dict, 'Pep')
        return Response(
            {"detail": "Generation of .xlsx file has begin. Expect an email with downloading link."},
            status=200
        )
