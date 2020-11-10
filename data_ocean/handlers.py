from corsheaders.signals import check_request_enabled
from django.urls import resolve
from django.conf import settings


def cors_allow_for_client_namespaces(sender, request, **kwargs):
    namespace = resolve(request.path).namespace
    return namespace in settings.NAMESPACES_FOR_CLIENTS


check_request_enabled.connect(cors_allow_for_client_namespaces)
