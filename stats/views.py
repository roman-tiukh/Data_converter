from datetime import timedelta, datetime
from django.db.models import Count
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import generics
from rest_framework import views
from rest_framework.response import Response
from .models import ApiUsageTracking
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

        now = datetime.now()
        current_month = ApiUsageTracking.objects.filter(
            user=request.user,
            timestamp__month=now.month,
            timestamp__year=now.year,
        ).count()

        prev_month = ApiUsageTracking.objects.filter(
            user=request.user,
            timestamp__month=12 if now.month == 1 else now.month - 1,
            timestamp__year=now.year - 1 if now.month == 1 else now.year,
        ).count()

        return Response({
            'days': days,
            'current_month': current_month,
            'prev_month': prev_month,
        }, status=200)


class TopKvedsView(generics.ListAPIView):
    # permission_classes = [AllowAny]
    queryset = (CompanyToKved.objects.select_related(
        'kved', 'kved__group', 'kved__section', 'kved__division',
    ).values('kved').annotate(
        count_kved=Count('kved')
    ).order_by('-count_kved')[:10])
    serializer_class = TopKvedSerializer
    pagination_class = None

    @method_decorator(cache_page(60 * 60 * 24))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
