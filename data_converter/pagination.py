import math
from collections import OrderedDict

from django.conf import settings
from django.core.paginator import Paginator
from django.core.cache import caches
from django.utils.functional import cached_property
from drf_yasg import openapi
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'last_page': math.ceil(self.page.paginator.count / self.page.paginator.per_page) or 1,
            'results': data,
        })

    def get_paginated_response_schema(self, schema):
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties=OrderedDict((
                ('count', openapi.Schema(
                    description='The number of objects matching the request.',
                    type=openapi.TYPE_INTEGER)
                 ),
                ('last_page', openapi.Schema(
                    description='The last page with data you can go to.',
                    type=openapi.TYPE_INTEGER)
                 ),
                ('results', schema),
            )),
            required=['results']
        )

    def get_schema_fields(self, view):
        return [
            openapi.Parameter(
                name='page',
                in_=openapi.IN_QUERY,
                description="A page number within the paginated result set.",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                name='page_size',
                in_=openapi.IN_QUERY,
                description="Number of results to return per page. Default=10, maximum size=100.",
                type=openapi.TYPE_INTEGER)
        ]


class CachedCountsPaginator(Paginator):
    cache_timeout = 60 * 60 * 24  # 24 hours

    def __init__(self, *args, request, **kwargs):
        self.request = request
        self.insensitive_keys = (
            CustomPagination.page_query_param,
            CustomPagination.page_size_query_param,
            'omit',
            'fields',
            'format',
            'o',
        )
        super().__init__(*args, **kwargs)

    def generate_key(self):
        key_params = {}
        for key, values in sorted(dict(self.request.GET).items()):
            if key in self.insensitive_keys:
                continue

            is_empty = True
            for v in values:
                if v == '':
                    continue
                is_empty = False
                break

            if not is_empty:
                key_params[key] = sorted(values)

        return f"{self.request.path}?{str(key_params).replace(' ', '')}"

    @cached_property
    def count(self):
        if 'counts' not in settings.CACHES:
            return super().count

        cache = caches['counts']
        cache_key = self.generate_key()
        count = cache.get(cache_key)
        if count is not None:
            return count
        count = super().count
        cache.set(cache_key, count, self.cache_timeout)
        return count


class CachedCountPagination(CustomPagination):
    # django_paginator_class = CachedCountsPaginator

    def django_paginator_class(self, queryset, page_size):
        return CachedCountsPaginator(queryset, page_size, request=self.request)

    def paginate_queryset(self, queryset, request, view=None):
        self.request = request
        return super().paginate_queryset(queryset, request, view)
