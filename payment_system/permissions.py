from django.utils import timezone
from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS
from rest_framework.request import Request
from django.conf import settings

from .models import (
    Project,
    ProjectSubscription,
)


class ProjectPermission(permissions.BasePermission):
    """
    Check if user have access to project.
    """

    def has_object_permission(self, request, view, obj: Project):
        user = request.user
        if user in obj.users.all():
            if request.method in SAFE_METHODS:
                return obj.has_read_perms(user=user)
            else:
                return obj.has_write_perms(user=user)
        return False


class AccessFromProjectToken(permissions.BasePermission):
    def has_permission(self, request: Request, view):
        # auth_header = request.headers.get('authorization')
        # if not auth_header or type(auth_header) != str:
        #     return False
        # auth_words = auth_header.split()
        # if len(auth_words) != 2:
        #     return False
        #
        # keyword = auth_words[0]
        # token = auth_words[1]
        #
        # try:
        #     project = Project.objects.get(token=token)
        # except Project.DoesNotExist:
        #     return False
        #
        # current_p2s = project.active_p2s
        #
        # if keyword == settings.PROJECT_TOKEN_KEYWORD:
        #     if current_p2s.requests_left <= 0:
        #         return False
        # elif keyword == settings.PROJECT_PLATFORM_TOKEN_KEYWORD:
        #     if current_p2s.platform_requests_left <= 0:
        #         return False
        # else:
        #     return False
        #
        # if current_p2s.expiring_date <= timezone.localdate():
        #     current_p2s.expire()
        #
        # request._request.token_keyword = keyword
        # request._request.project = project
        #
        # return True

        project: Project = getattr(request, 'project', None)
        return bool(project and isinstance(project, Project))
