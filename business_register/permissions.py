from urllib.parse import urlparse

from rest_framework.permissions import BasePermission
from django.conf import settings


class CheckTokenPermissionMixin:
    keyword = None

    def check_token(self, request, allowed_token):
        assert self.keyword
        request_token = request.headers.get('Authorization')
        if request_token:
            request_token = request_token.split()
            if len(request_token) == 2 and request_token[0] == self.keyword \
                    and request_token[1] == allowed_token:
                return True
        return False


class PepSchemaToken(CheckTokenPermissionMixin, BasePermission):
    keyword = 'PEP'

    def has_permission(self, request, view):
        tokens = settings.PEP_SCHEMA_TOKENS or {}
        referer = request.headers.get('referer')
        if not referer:
            return False

        referer_host = urlparse(referer).hostname
        if referer_host not in tokens:
            return False

        allowed_token = tokens[referer_host]
        return self.check_token(request, allowed_token)


class PepServerToken(CheckTokenPermissionMixin, BasePermission):
    keyword = 'PEP'

    def has_permission(self, request, view):
        return self.check_token(request, settings.PEP_SERVER_TOKEN)
