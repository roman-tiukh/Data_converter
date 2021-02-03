from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import SearchFilter

from data_ocean.views import CachedViewSetMixin, RegisterViewMixin
from location_register.filters import RatuStreetFilterSet
from location_register.models.ratu_models import RatuRegion, RatuDistrict, RatuCity, RatuCityDistrict, RatuStreet
from location_register.serializers.ratu_serializers import RatuRegionSerializer, RatuDistrictSerializer, \
    RatuCitySerializer, RatuCityDistrictSerializer, \
    RatuStreetSerializer


class RatuRegionView(RegisterViewMixin,
                     CachedViewSetMixin,
                     viewsets.ReadOnlyModelViewSet):
    queryset = RatuRegion.objects.all()
    serializer_class = RatuRegionSerializer


class RatuDistrictView(RegisterViewMixin,
                       CachedViewSetMixin,
                       viewsets.ReadOnlyModelViewSet):
    queryset = RatuDistrict.objects.all()
    serializer_class = RatuDistrictSerializer


class RatuCityView(RegisterViewMixin,
                   CachedViewSetMixin,
                   viewsets.ReadOnlyModelViewSet):
    queryset = RatuCity.objects.all()
    serializer_class = RatuCitySerializer


class RatuCityDistrictView(RegisterViewMixin,
                           CachedViewSetMixin,
                           viewsets.ReadOnlyModelViewSet):
    queryset = RatuCityDistrict.objects.all()
    serializer_class = RatuCityDistrictSerializer


class RatuStreetView(RegisterViewMixin,
                     CachedViewSetMixin,
                     viewsets.ReadOnlyModelViewSet):
    queryset = RatuStreet.objects.select_related(
        'region', 'district', 'city', 'citydistrict'
    ).all()
    serializer_class = RatuStreetSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset = RatuStreetFilterSet
    search_fields = ('name',)
