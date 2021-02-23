from datetime import datetime, timedelta
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from business_register.filters import PepFilterSet
from business_register.models.pep_models import Pep
from business_register.permissions import PepSchemaToken
from business_register.serializers.company_and_pep_serializers import PepListSerializer, PepDetailSerializer
from data_converter.filter import DODjangoFilterBackend
from data_ocean.views import CachedViewSetMixin, RegisterViewMixin
from data_ocean.export import Export_to_xlsx


@method_decorator(name='retrieve', decorator=swagger_auto_schema(tags=['pep']))
@method_decorator(name='list', decorator=swagger_auto_schema(tags=['pep']))
@method_decorator(name='retrieve_by_source_id', decorator=swagger_auto_schema(auto_schema=None))
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
        before_date = datetime.strptime(request.GET['updated_at_before'], '%Y-%m-%d')
        after_date = datetime.strptime(request.GET['updated_at_after'], '%Y-%m-%d')
        if (before_date and after_date) and timedelta(days=0) < before_date - after_date <= timedelta(days=31):
            queryset = self.filter_queryset(self.get_queryset())
        else:
            return HttpResponse('Use "updated_at_after" & "updated_at_before" GET parameters. '
                                'The time period for data exported in .xlsx cannot exceed 31 days.',
                                content_type="text/plain")
        export_dict = {
            'Full Name': ['fullname', 40],
            'Status': ['is_pep', 20],
            'PEP Type': ['pep_type', 30],
            'Last Job Title': ['last_job_title', 40],
            'Last Employer': ['last_employer', 40]
        }
        worksheet_title = 'PEP'
        export_file_path = Export_to_xlsx().export(queryset, export_dict, worksheet_title)
        if export_file_path:
            return HttpResponse(export_file_path, content_type="text/plain")
