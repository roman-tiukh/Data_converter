from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from drf_yasg.generators import OpenAPISchemaGenerator, EndpointEnumerator
from drf_yasg.inspectors import SwaggerAutoSchema
from drf_yasg.utils import swagger_auto_schema
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions, viewsets
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from django.conf import settings
from data_converter import settings_local
from data_converter.settings_local import BACKEND_SITE_URL
from data_ocean.filters import RegisterFilter
from data_ocean.models import Register
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from data_ocean.serializers import RegisterSerializer
from rest_framework.permissions import IsAuthenticated
from payment_system.permissions import AccessFromProjectToken


class CachedViewMixin:
    @method_decorator(cache_page(settings.CACHE_MIDDLEWARE_SECONDS))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class CachedViewSetMixin:
    @method_decorator(cache_page(settings.CACHE_MIDDLEWARE_SECONDS))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(settings.CACHE_MIDDLEWARE_SECONDS))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class RegisterViewMixin:
    # TODO: remove IsAuthenticated after project-tokens will be finished.
    permission_classes = [IsAuthenticated | AccessFromProjectToken]


class DOEndpointEnumerator(EndpointEnumerator):
    def should_include_endpoint(self, path, callback, app_name='',
                                namespace='', url_name=None):
        if namespace not in settings.NAMESPACES_FOR_CLIENTS:
            return False
        return super().should_include_endpoint(
            path, callback, app_name=app_name,
            namespace=namespace, url_name=url_name
        )


class DOOpenAPISchemaGenerator(OpenAPISchemaGenerator):
    endpoint_enumerator_class = DOEndpointEnumerator


SchemaView = get_schema_view(
    openapi.Info(
        title="DataOcean",
        default_version='v1',
        description=(
            f"<div><a href='{settings_local.FRONTEND_SITE_URL}/docs/TermsAndConditionsEn.html' target= '_blank'>Terms and conditions |<a/>"
            f"<a href='{settings_local.FRONTEND_SITE_URL}/docs/TermsAndConditionsUk.html' target= '_blank'> Правила та умови<a/><div/>"
            '<p style="font-style: normal; cursor: default; color: #000000">An easy access to the data, using the Rest API for software developers.<br>'
            'Зручний доступ до даних за допомогою Rest API для розробників програмного забезпечення.<p/>'
        ),
        contact=openapi.Contact(email="info@dataocean.us"),
    ),
    url=f'{BACKEND_SITE_URL}',
    generator_class=DOOpenAPISchemaGenerator,
    public=True,
    permission_classes=(permissions.AllowAny,),
)


class Views(GenericAPIView):
    def get(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            result = self.get_paginated_response(serializer.data)
            data = result.data  # pagination data
        else:
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data
        return Response(data)


@method_decorator(name='retrieve', decorator=swagger_auto_schema(auto_schema=None))
@method_decorator(name='list', decorator=swagger_auto_schema(auto_schema=None))
class RegisterView(RegisterViewMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Register.objects.all()
    serializer_class = RegisterSerializer
    filterset_class = RegisterFilter
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['name', 'source_register_id', 'status', ]


class DOAutoSchemaClass(SwaggerAutoSchema):
    def get_operation(self, operation_keys=None):
        operation = super().get_operation(operation_keys)
        example_curl = None
        if operation_keys[-1] == 'list':
            example_curl = f"curl -X GET -H 'Authorization: DataOcean {{token}}' \\\n{settings_local.BACKEND_SITE_URL}/" \
                           f"api/{'/'.join(operation_keys[:-1])}/"
            example_python = "import requests\nfrom pprint import pprint\n\n" \
                             f"response = requests.get(\n\t'{settings_local.BACKEND_SITE_URL}/api/{'/'.join(operation_keys[:-1])}/',\n" \
                             f"\tparams={{'page': 1, 'page_size': 20}},\n" \
                             f"\theaders={{'Authorization': 'DataOcean {{token}}'}},\n)\n\n" \
                             "pprint(response.json())"
        elif operation_keys[-1] == 'read':
            example_curl = f"curl -X GET -H 'Authorization: DataOcean {{token}}' \\\n{settings_local.BACKEND_SITE_URL}/" \
                           f"api/{'/'.join(operation_keys[:-1])}/{{id}}/"
            example_python = "import requests\nfrom pprint import pprint\n\n" \
                             f"response = requests.get(\n\t'{settings_local.BACKEND_SITE_URL}/api/{'/'.join(operation_keys[:-1])}/{{id}}/',\n" \
                             f"\theaders={{'Authorization': 'DataOcean {{token}}'}},\n)\n\n" \
                             "pprint(response.json())"
        if example_curl:
            operation.update({
                'x-code-samples': [
                    {
                        "lang": "curl",
                        "source": example_curl
                    },
                    {
                        "lang": "python",
                        "source": example_python
                    },
                ],
            })
        return operation

    def get_responses(self):
        responses = super().get_responses()
        responses.update({
            400: {
                'description': "Bad Request",
                'schema': {
                    'type': openapi.TYPE_OBJECT,
                    'properties': {
                        'error': {
                            'type': openapi.TYPE_STRING,
                            'description': 'Response status code indicates that the server cannot or will not process'
                                           ' the request due to something that is perceived to be a client error (e.g., '
                                           'malformed request syntax, invalid request message framing, or deceptive'
                                           ' request routing).',
                        }
                    },
                    'examples': [{'detail': 'Bad Request'}],
                },
            },
            403: {
                'description': 'Forbidden',
                'schema': {
                    'type': openapi.TYPE_OBJECT,
                    'properties': {
                        'error': {
                            'type': openapi.TYPE_STRING,
                            'description': 'Client error status response code indicates that the server understood the'
                                           ' request but refuses to authorize it. This status is similar to 401, but in'
                                           ' this case, re-authenticating will make no difference. The access is'
                                           ' permanently forbidden and tied to the application logic, such as'
                                           ' insufficient rights to a resource.',
                        },
                    },
                    'examples': [{"detail": 'Authentication credentials were not provided.'}],
                },
            },
            404: {
                'description': 'Not Found',
                'schema': {
                    'type': openapi.TYPE_OBJECT,
                    'properties': {
                        'error': {
                            'type': openapi.TYPE_STRING,
                            'description': 'The requested resource could not be found but may be available again in the'
                                           ' future. Subsequent requests by the client are permissible.',
                        }
                    },
                    'examples': [{"detail": 'Not found.'}],
                },
            },
            500: {
                'description': 'Internal Server Error',
                'schema': {
                    'type': openapi.TYPE_OBJECT,
                    'properties': {
                        'error': {
                            'type': openapi.TYPE_STRING,
                            'description': 'Server error response code indicates that the server encountered an '
                                           'unexpected condition that prevented it from fulfilling the request.',
                        },
                    },
                    'examples': [{"detail": 'Server Error (500)'}],
                },
            },
        })
        return responses
