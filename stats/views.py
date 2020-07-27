from datetime import timedelta
from django.utils import timezone
from rest_framework import views
from rest_framework.response import Response
from stats import logic


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
