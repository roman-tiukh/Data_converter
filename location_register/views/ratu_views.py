from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.filters import SearchFilter

from data_ocean.views import CachedViewSetMixin, RegisterViewMixin
from location_register.filters import RatuStreetFilterSet
from location_register.models.ratu_models import RatuRegion, RatuDistrict, RatuCity, RatuCityDistrict, RatuStreet
from location_register.serializers.ratu_serializers import RatuRegionSerializer, RatuDistrictSerializer, \
    RatuCitySerializer, RatuCityDistrictSerializer, \
    RatuStreetSerializer


@method_decorator(name='retrieve', decorator=swagger_auto_schema(tags=['location register']))
@method_decorator(name='list', decorator=swagger_auto_schema(tags=['location register']))
class RatuRegionView(RegisterViewMixin,
                     CachedViewSetMixin,
                     viewsets.ReadOnlyModelViewSet):
    queryset = RatuRegion.objects.all()
    serializer_class = RatuRegionSerializer


@method_decorator(name='retrieve', decorator=swagger_auto_schema(tags=['location register']))
@method_decorator(name='list', decorator=swagger_auto_schema(tags=['location register']))
class RatuDistrictView(RegisterViewMixin,
                       CachedViewSetMixin,
                       viewsets.ReadOnlyModelViewSet):
    queryset = RatuDistrict.objects.all()
    serializer_class = RatuDistrictSerializer


@method_decorator(name='retrieve', decorator=swagger_auto_schema(tags=['location register']))
@method_decorator(name='list', decorator=swagger_auto_schema(tags=['location register']))
class RatuCityView(RegisterViewMixin,
                   CachedViewSetMixin,
                   viewsets.ReadOnlyModelViewSet):
    queryset = RatuCity.objects.all()
    serializer_class = RatuCitySerializer


@method_decorator(name='retrieve', decorator=swagger_auto_schema(tags=['location register']))
@method_decorator(name='list', decorator=swagger_auto_schema(tags=['location register']))
class RatuCityDistrictView(RegisterViewMixin,
                           CachedViewSetMixin,
                           viewsets.ReadOnlyModelViewSet):
    queryset = RatuCityDistrict.objects.all()
    serializer_class = RatuCityDistrictSerializer


@method_decorator(name='retrieve', decorator=swagger_auto_schema(tags=['location register']))
@method_decorator(name='list', decorator=swagger_auto_schema(tags=['location register']))
class RatuStreetView(RegisterViewMixin,
                     CachedViewSetMixin,
                     viewsets.ReadOnlyModelViewSet):
    queryset = RatuStreet.objects.select_related(
        'region', 'district', 'city', 'citydistrict'
    ).all()
    serializer_class = RatuStreetSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_class = RatuStreetFilterSet
    search_fields = ('name',)
