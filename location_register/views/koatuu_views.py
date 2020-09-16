from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import SearchFilter

from data_ocean.views import CachedViewMixin
from location_register.filters import (KoatuuFirstLevelFilterSet, KoatuuSecondLevelFilterSet,
                                       KoatuuThirdLevelFilterSet, KoatuuFourthLevelFilterSet)
from location_register.models.koatuu_models import (KoatuuFirstLevel, KoatuuSecondLevel,
                                                    KoatuuThirdLevel, KoatuuFourthLevel)
from location_register.serializers.koatuu_serializers import (KoatuuFirstLevelSerializer,
                                                              KoatuuSecondLevelSerializer,
                                                              KoatuuThirdLevelSerializer,
                                                              KoatuuFourthLevelSerializer)


class KoatuuFirstLevelViewSet(CachedViewMixin, viewsets.ReadOnlyModelViewSet):
    queryset = KoatuuFirstLevel.objects.prefetch_related('second_level_places').all()
    serializer_class = KoatuuFirstLevelSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset = KoatuuFirstLevelFilterSet
    search_fields = ('code', 'name')


class KoatuuSecondLevelViewSet(CachedViewMixin, viewsets.ReadOnlyModelViewSet):
    queryset = (KoatuuSecondLevel.objects.select_related('first_level')
                .prefetch_related('third_level_places')
                .all())
    serializer_class = KoatuuSecondLevelSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset = KoatuuSecondLevelFilterSet
    search_fields = ('code', 'name')


class KoatuuThirdLevelViewSet(CachedViewMixin, viewsets.ReadOnlyModelViewSet):
    queryset = (KoatuuThirdLevel.objects.select_related('first_level', 'second_level')
                .prefetch_related('fourth_level_places')
                .all())
    serializer_class = KoatuuThirdLevelSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset = KoatuuThirdLevelFilterSet
    search_fields = ('code', 'name')


class KoatuuFourthLevelViewSet(CachedViewMixin, viewsets.ReadOnlyModelViewSet):
    queryset = KoatuuFourthLevel.objects.select_related(
        'first_level', 'second_level', 'third_level', 'category').all()
    serializer_class = KoatuuFourthLevelSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset = KoatuuFourthLevelFilterSet
    search_fields = ('code', 'name')
