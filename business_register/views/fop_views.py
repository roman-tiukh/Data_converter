from rest_framework import viewsets

from business_register.models.fop_models import Fop
from business_register.serializers.fop_serializers import FopSerializer
from data_ocean.views import CachedViewMixin


class FopView(CachedViewMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Fop.objects.all()
    serializer_class = FopSerializer
