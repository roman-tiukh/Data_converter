from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.inspectors import DjangoRestResponsePagination, CoreAPICompatInspector
from rest_framework.filters import SearchFilter


class DODjangoRestResponsePagination(DjangoRestResponsePagination):

    def get_paginator_parameters(self, paginator):
        return paginator.get_schema_fields(self.view)

    def get_paginated_response(self, paginator, response_schema):
        return paginator.get_paginated_response_schema(response_schema)


class DjangoFilterDescriptionInspector(CoreAPICompatInspector):
    def get_filter_parameters(self, filter_backend):
        params = super().get_filter_parameters(filter_backend)
        if isinstance(filter_backend, DjangoFilterBackend):
            for param in params:
                if not param.get('description', ''):
                    param.description = f"Filter the returned list by {param.name}"
        if isinstance(filter_backend, SearchFilter):
            fields = getattr(self.view, 'search_fields')
            fields = ', '.join(fields)
            params[0].description = f"Search by {fields}"

        return params
