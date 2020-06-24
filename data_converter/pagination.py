import math
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'last_page': math.ceil(self.request.GET.get(
                'last_page',
                self.page.paginator.count/int(self.request.GET.get('page_size', self.page_size))
            )),
            'results': data,
        })
