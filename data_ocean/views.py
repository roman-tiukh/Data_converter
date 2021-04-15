from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from drf_dynamic_fields import DynamicFieldsMixin
from drf_yasg.generators import OpenAPISchemaGenerator, EndpointEnumerator
from drf_yasg.inspectors import SwaggerAutoSchema
from drf_yasg.utils import swagger_auto_schema
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions, viewsets
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from django.conf import settings
from data_ocean.filters import RegisterFilter
from data_ocean.models import Register
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from data_ocean.serializers import RegisterSerializer
from rest_framework.permissions import IsAuthenticated
from payment_system.permissions import AccessFromProjectToken, ServiceTokenPermission


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
    permission_classes = [AccessFromProjectToken | ServiceTokenPermission]

    def get_permissions(self):
        if settings.DEBUG:
            permission_classes = [self.permission_classes[0] | IsAuthenticated]
            return [permission() for permission in permission_classes]
        return super().get_permissions()


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
            f'<div><a href=\'{settings.FRONTEND_SITE_URL}/docs/TermsAndConditionsEn.html\' target= \'_blank\'>Terms and '
            f'conditions |</a><a href=\'{settings.FRONTEND_SITE_URL}/docs/TermsAndConditionsUk.html\' target= \'_blank\'>'
            ' Правила та умови</a><div/><p style="font-style: normal; cursor: default; color: #000000">An easy access '
            'to the data, using the Rest API for software developers.<br>Зручний доступ до даних за допомогою Rest API '
            'для розробників програмного забезпечення.<p/><p style="font-style: normal; cursor: default; color: #000000">'
            f'Download API samples Postman collection: <a download target=\'_blank\' href=\'{settings.STATIC_URL}'
            f'DataOcean - pep_list v4.postman_collection.json\' class=\'sc-fzobTh cbdZGY\'>Download</a><p/>'
            '<p style="font-style: normal; cursor: default; color: #000000">For former <a href=\'https://pep.org.ua/\'>'
            f'pep.org.ua</a> users: <a download target=\'_blank\' href=\'{settings.STATIC_URL}For former pep.org.ua '
            'users.zip\'class=\'sc-fzobTh cbdZGY\'>Download</a><p/>'
        ),
        contact=openapi.Contact(email="info@dataocean.us"),
        x_logo={
            'url': f'{settings.STATIC_URL}logo.png',
            'backgroundColor': '#FFFFFF"',
            'href': f'{settings.FRONTEND_SITE_URL}'
        }
    ),
    url=f'{settings.BACKEND_SITE_URL}',
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
class RegisterView(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Register.objects.all()
    serializer_class = RegisterSerializer
    filterset_class = RegisterFilter
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['name', 'name_eng', ]


class DOAutoSchemaClass(SwaggerAutoSchema):
    def get_operation(self, operation_keys=None):
        operation = super().get_operation(operation_keys)
        example_curl = None
        example_python = None
        example_php = None
        example_java = None
        if operation_keys[-1] == 'list':
            example_curl = f"curl -X GET -H 'Authorization: DataOcean {{token}}' \\\n{settings.BACKEND_SITE_URL}/" \
                           f"api/{'/'.join(operation_keys[:-1])}/"
            example_python = "import requests\nfrom pprint import pprint\n\n" \
                             f"response = requests.get(\n\t'{settings.BACKEND_SITE_URL}/api/{'/'.join(operation_keys[:-1])}/',\n" \
                             f"\tparams={{'page': 1, 'page_size': 20}},\n" \
                             f"\theaders={{'Authorization': 'DataOcean {{token}}'}},\n)\n\n" \
                             "pprint(response.json())"
            example_php = "$opts = [\n\t'https' => [\n\t\t'method' => 'GET',\n\t\t'header' => 'Accept: application/json'," \
                          "\n\t\t\t    'Authorization: DataOcean {token}', \n\t\t\t    'Content-type: application/json'," \
                          f"\n\t\t\t    'Host: {str(settings.BACKEND_SITE_URL)[8:]}'\n\t]\n];\n$context = stream_" \
                          f"context_create($opts);\n$response = file_get_contents('{settings.BACKEND_SITE_URL}/api/" \
                          f"{'/'.join(operation_keys[:-1])}', false, $context);\nvar_dump($response);"
            example_java = "HttpRequest request = HttpRequest.newBuilder()\n" \
                           f"\t.uri(new URI('{settings.BACKEND_SITE_URL}/api/{'/'.join(operation_keys[:-1])}/'))\n" \
                           "\t.header('Authorization', 'DataOcean {token}')\n" \
                           "\t.GET()\n" \
                           "\t.build();\n" \
                           "HttpResponse<String> response = HttpClient\n" \
                           "\t.newBuilder()\n" \
                           "\t.build();\n" \
                           "\t.send(request, HttpResponse.BodyHandler.asString());"

        elif operation_keys[-1] == 'read':
            example_curl = f"curl -X GET -H 'Authorization: DataOcean {{token}}' \\\n{settings.BACKEND_SITE_URL}/" \
                           f"api/{'/'.join(operation_keys[:-1])}/{{id}}/"
            example_python = "import requests\nfrom pprint import pprint\n\n" \
                             f"response = requests.get(\n\t'{settings.BACKEND_SITE_URL}/api/{'/'.join(operation_keys[:-1])}/{{id}}/',\n" \
                             f"\theaders={{'Authorization': 'DataOcean {{token}}'}},\n)\n\n" \
                             "pprint(response.json())"
            example_php = "$opts = [\n\t'https' => [\n\t\t'method' => 'GET',\n\t\t'header' => 'Accept: application/json'," \
                          "\n\t\t\t    'Authorization: DataOcean {token}', \n\t\t\t    'Content-type: application/json'," \
                          f"\n\t\t\t    'Host: {str(settings.BACKEND_SITE_URL)[8:]}'\n\t]\n];\n$context = stream_" \
                          f"context_create($opts);\n$response = file_get_contents('{settings.BACKEND_SITE_URL}/api/" \
                          f"{'/'.join(operation_keys[:-1])}/{{id}}', false, $context);\nvar_dump($response);"
            example_java = "HttpRequest request = HttpRequest.newBuilder()\n" \
                           f"\t.uri(new URI('{settings.BACKEND_SITE_URL}/api/{'/'.join(operation_keys[:-1])}/{{id}}/'))\n" \
                           "\t.header('Authorization', 'DataOcean {token}')\n" \
                           "\t.GET()\n" \
                           "\t.build();\n" \
                           "HttpResponse<String> response = HttpClient\n" \
                           "\t.newBuilder()\n" \
                           "\t.build()\n" \
                           "\t.send(request, HttpResponse.BodyHandler.asString());"

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
                    {
                        "lang": "php",
                        "source": example_php
                    },
                    {
                        "lang": "java",
                        'source': example_java
                    }
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

    def add_manual_parameters(self, parameters):
        fields = super().add_manual_parameters(parameters)
        fields.append(
            openapi.Parameter(
                name='format',
                in_=openapi.IN_QUERY,
                description='You can receive data in json and xml format. The default format = json. To get data in xml'
                            ' format, specify ?format=xml in the query parameters.',
                type=openapi.TYPE_STRING
            )
        )
        if DynamicFieldsMixin in self.view.serializer_class.__bases__:
            fields.append(
                openapi.Parameter(
                    name='fields',
                    in_=openapi.IN_QUERY,
                    description='A parameter that allows you to select the fields that will be returned as a result of '
                                'request. For example, if you need to select the id and fullname fields: ?fields=id,fullname. '
                                '<br/> In general:<br/> ?fields=fieldname1,fieldname2, etc. The recording is made through '
                                'a comma without a space.',
                    type=openapi.TYPE_STRING,
                )
            )
        return fields
