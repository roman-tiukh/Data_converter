import math
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
