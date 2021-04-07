from rest_framework.permissions import IsAuthenticated

from payment_system.models import UserProject


class ExportPermission(IsAuthenticated):
    """
       Allows access only to authenticated users with active and not default project(s).
    """

    def has_permission(self, request, view):
        return bool(super().has_permission() and UserProject.objects.filter(
            user=request.user, is_default=False, status='Active').count() > 0)
