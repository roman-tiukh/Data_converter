from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.inspectors import DjangoRestResponsePagination, CoreAPICompatInspector, NotHandled
from rest_framework.filters import SearchFilter


class DODjangoRestResponsePagination(DjangoRestResponsePagination):

    def get_paginator_parameters(self, paginator):
        return paginator.get_schema_fields(self.view)

    def get_paginated_response(self, paginator, response_schema):
        return paginator.get_paginated_response_schema(response_schema)


class DjangoFilterDescriptionInspector(CoreAPICompatInspector, SearchFilter):
    def get_filter_parameters(self, filter_backend):
        if isinstance(filter_backend, DjangoFilterBackend):
            result = super().get_filter_parameters(filter_backend)
            for param in result:
                if not param.get('description', ''):
                    param.description = f"Filter the returned list by {param.name}"
            return result
        if isinstance(filter_backend, SearchFilter):
            result = super().get_filter_parameters(filter_backend)
            fields = super().get_search_fields(self.view, self.request)
            fields = str(fields).replace('(', ' ')
            fields = str(fields).replace(')', ' ')
            for param in result:
                param.description = f"Search by {fields}"
                return result

        return NotHandled
