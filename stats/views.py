from datetime import timedelta

from django.db.models import Count
from django.utils import timezone
from rest_framework import generics
from rest_framework import views
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from business_register.models.company_models import CompanyToKved
from stats import logic
from stats.serializers import TopKvedSerializer


class ApiUsageMeView(views.APIView):
    def get(self, request):
        date_to = timezone.now()
        date_from = date_to - timedelta(days=30)

        days = logic.get_api_usage_by_day(
            date_from=date_from,
            date_to=date_to,
            user_id=request.user.id
        )

        return Response({'days': days}, status=200)


class TopKvedsView(generics.ListAPIView):
    # permission_classes = [AllowAny]
    queryset = (CompanyToKved.objects.select_related(
        'kved', 'kved__group', 'kved__section', 'kved__division',
    ).values('kved').annotate(
        count_kved=Count('kved')
    ).order_by('-count_kved')[:10])
    serializer_class = TopKvedSerializer
