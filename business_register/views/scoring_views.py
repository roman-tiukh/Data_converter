from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from business_register.filters import PepScoringFilterSet
from business_register.models.declaration_models import PepScoring
from business_register.permissions import PepServerToken
from business_register.serializers.scoring_serializers import PepScoringSerializer
from data_converter.filter import DODjangoFilterBackend


@method_decorator(name='list', decorator=swagger_auto_schema(tags=['business register'], auto_schema=None))
class PepScoringListView(ListAPIView):
    permission_classes = [PepServerToken]
    queryset = PepScoring.objects.order_by('-calculation_datetime')
    serializer_class = PepScoringSerializer
    filter_backends = (DODjangoFilterBackend,)
    filterset_class = PepScoringFilterSet
