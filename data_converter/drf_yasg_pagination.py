from drf_yasg.inspectors import DjangoRestResponsePagination


class DODjangoRestResponsePagination(DjangoRestResponsePagination):

    def get_paginator_parameters(self, paginator):
        return paginator.get_schema_fields(self.view)

    def get_paginated_response(self, paginator, response_schema):
        return paginator.get_paginated_response_schema(response_schema)

