from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from drf_yasg.generators import OpenAPISchemaGenerator, EndpointEnumerator
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions, viewsets
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from django.conf import settings
from data_converter import settings_local
from data_ocean.filters import RegisterFilter
from data_ocean.models import Register
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from data_ocean.serializers import RegisterSerializer
from rest_framework.permissions import IsAuthenticated
from payment_system.permissions import AccessFromProjectToken


class CachedViewMixin:
    @method_decorator(cache_page(60 * 60 * 24))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


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


class RegisterView(RegisterViewMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Register.objects.all()
    serializer_class = RegisterSerializer
    filterset_class = RegisterFilter
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['name', 'source_register_id', 'status', ]
