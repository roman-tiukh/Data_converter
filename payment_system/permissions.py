import time

from django.utils import timezone
from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS
from rest_framework.request import Request
from django.conf import settings
from rest_framework.exceptions import Throttled
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


class ServiceTokenPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        auth_header = request.headers.get('authorization')
        if not auth_header or type(auth_header) != str:
            return False
        auth_words = auth_header.split()
        if len(auth_words) != 2:
            return False

        keyword = auth_words[0]
        token = auth_words[1]
        if keyword == 'Service' and token == settings.SERVICE_TOKEN:
            return True
        return False


class AccessFromProjectToken(permissions.BasePermission):
    decrease_requests_counter = True

    def has_permission(self, request: Request, view):
        project: Project = getattr(request, 'project', None)
        request._request._decrease_requests_counter = self.decrease_requests_counter
        return bool(project and isinstance(project, Project))


class PepChecksPermission(AccessFromProjectToken):
    decrease_requests_counter = False

    def has_permission(self, request: Request, view):
        has_project_perms = super().has_permission(request, view)
        if not has_project_perms:
            return False

        current_p2s: ProjectSubscription = request.current_p2s
        if not current_p2s.subscription.pep_checks:
            return False

        unix_now = int(time.time())
        unix_minute_now = unix_now // 60
        if unix_minute_now > current_p2s.pep_checks_minute:
            current_p2s.pep_checks_minute = unix_minute_now
            current_p2s.pep_checks_count_per_minute = 1
            current_p2s.save(update_fields=[
                'pep_checks_minute',
                'pep_checks_count_per_minute',
            ])
            return True
        elif current_p2s.pep_checks_count_per_minute >= current_p2s.subscription.pep_checks_per_minute:
            raise Throttled(wait=60 - (unix_now - (current_p2s.pep_checks_minute * 60)))
        else:
            current_p2s.pep_checks_count_per_minute += 1
            current_p2s.save(update_fields=['pep_checks_count_per_minute'])
            return True
