from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS

from .models import (
    Project,
)


class ProjectPermission(permissions.BasePermission):
    """
    Check if user have access to project.
    """

    def has_object_permission(self, request, view, obj: Project):
        user = request.user
        if user in obj.users.all():
            if request.method in SAFE_METHODS:
                return True
            else:
                return obj.has_write_perms(user=user)
        return False
