from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from business_register.filters import KvedFilterSet
from business_register.models.kved_models import Kved
from business_register.serializers.kved_serializers import KvedDetailSerializer
from data_ocean.views import RegisterViewMixin, CachedViewSetMixin


@method_decorator(name='retrieve', decorator=swagger_auto_schema(tags=['kved']))
@method_decorator(name='list', decorator=swagger_auto_schema(tags=['kved']))
class KvedViewSet(RegisterViewMixin,
                  CachedViewSetMixin,
                  viewsets.ReadOnlyModelViewSet):
    queryset = Kved.objects.select_related('group', 'division', 'section').exclude(is_valid=False)
    serializer_class = KvedDetailSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_class = KvedFilterSet
    search_fields = ('code', 'name')
