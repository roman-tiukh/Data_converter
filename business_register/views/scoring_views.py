from django.http import Http404
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import ListAPIView

from business_register.filters import PepScoringFilterSet
from business_register.models.declaration_models import PepScoring, Declaration
from business_register.permissions import PepServerToken
from business_register.serializers.scoring_serializers import PepScoringSerializer
from data_converter.filter import DODjangoFilterBackend


@method_decorator(name='list', decorator=swagger_auto_schema(auto_schema=None))
class PepScoringListView(ListAPIView):
    permission_classes = [PepServerToken]
    queryset = PepScoring.objects.filter(declaration__type=Declaration.ANNUAL).order_by('-pep_id', '-score')
    serializer_class = PepScoringSerializer
    filter_backends = (DODjangoFilterBackend,)
    filterset_class = PepScoringFilterSet


@method_decorator(name='list', decorator=swagger_auto_schema(auto_schema=None))
class PepScoringDetailView(ListAPIView):
    permission_classes = [PepServerToken]
    serializer_class = PepScoringSerializer
    filter_backends = (DODjangoFilterBackend,)
    filterset_class = PepScoringFilterSet
    pagination_class = None

    def get_queryset(self):
        last_declaration = Declaration.objects.filter(
            pep__source_id=self.kwargs['source_id'],
            type=Declaration.ANNUAL,
        ).order_by('-submission_date').first()
        if not last_declaration:
            raise Http404
        return PepScoring.objects.select_related(
            'declaration'
        ).filter(
            declaration_id=last_declaration.id,
            score__gt=0,
        ).order_by('-score')
