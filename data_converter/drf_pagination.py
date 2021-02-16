from collections import OrderedDict

from drf_yasg import openapi
from drf_yasg.inspectors import PaginatorInspector


class DOResponsePaginationClass(PaginatorInspector):

    def get_paginator_parameters(self, paginator):
        return [
            openapi.Parameter('page', openapi.IN_QUERY, "A page number within the paginated result set.", False, None, openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, "Number of results to return per page. Default=10, maximum size=100", False, None, openapi.TYPE_INTEGER)
        ]

    def get_paginated_response(self, paginator, response_schema):
        paged_schema = openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties=OrderedDict((
                    ('count', openapi.Schema(type=openapi.TYPE_INTEGER)),
                    ('last_page', openapi.Schema(type=openapi.TYPE_INTEGER)),
                    ('results', response_schema),
                )),
                required=['results']
            )

        return paged_schema
