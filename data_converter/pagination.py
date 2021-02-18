import math
from collections import OrderedDict

from drf_yasg import openapi
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        page_size_from_get = int(self.request.GET.get(self.page_size_query_param, self.page_size))
        page_size = page_size_from_get if page_size_from_get <= self.max_page_size else self.max_page_size
        return Response({
            'count': self.page.paginator.count,
            'last_page': math.ceil(self.page.paginator.count / page_size),
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
