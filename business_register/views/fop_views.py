from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from business_register.filters import FopFilterSet
from business_register.models.fop_models import Fop
from business_register.serializers.fop_serializers import FopSerializer
from data_converter.pagination import CachedCountPagination
from data_ocean.permissions import IsAuthenticatedAndPaidSubscription
from data_ocean.views import CachedViewSetMixin, RegisterViewMixin
from rest_framework.filters import SearchFilter


@method_decorator(name='retrieve', decorator=swagger_auto_schema(tags=['business register']))
@method_decorator(name='list', decorator=swagger_auto_schema(tags=['business register']))
@method_decorator(name='export_to_xlsx', decorator=swagger_auto_schema(auto_schema=None))
class FopViewSet(RegisterViewMixin,
                 CachedViewSetMixin,
                 viewsets.ReadOnlyModelViewSet):
    pagination_class = CachedCountPagination
    queryset = Fop.objects.select_related(
        'status', 'authority'
    ).prefetch_related(
        'kveds', 'exchange_data'
    ).all()
    filter_backends = (DjangoFilterBackend, SearchFilter)
    serializer_class = FopSerializer
    filterset_class = FopFilterSet
    search_fields = ('fullname', 'address', 'status__name')

    @action(detail=False, url_path='xlsx', permission_classes=[IsAuthenticatedAndPaidSubscription])
    def export_to_xlsx(self, request):
        filterset =
