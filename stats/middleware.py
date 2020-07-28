from django.http import HttpRequest, HttpResponse
from .models import ApiUsageTracking
from django.conf import settings
from urllib.parse import urlparse


class ApiUsageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        referer = request.headers.get('referer', None)
        response: HttpResponse = self.get_response(request)

        def create_api_usage_object():
            ApiUsageTracking.objects.create(
                user=request.user,
                pathname=request.path,
                referer=referer or '',
            )

        if not request.user.is_anonymous and response.status_code // 100 == 2 \
                and request.path.startswith('/api/'):
            if referer:
                referer_host = urlparse(referer).hostname
                if referer_host not in settings.STATS_API_USAGE_REFERER_BLACKLIST:
                    create_api_usage_object()
            else:
                create_api_usage_object()

        return response
