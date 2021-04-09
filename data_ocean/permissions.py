from rest_framework.permissions import IsAuthenticated

from payment_system.models import UserProject


class IsAuthenticatedAndPaidSubscription(IsAuthenticated):
    """
       Allows access only to authenticated users with not disabled project(s) with paid subscription.
    """

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        for user_project in UserProject.objects.select_related('project').filter(
                user=request.user,
                status=UserProject.ACTIVE
        ):
            if not user_project.project.disabled_at and user_project.project.active_subscription.price > 0:
                return True
        return False
