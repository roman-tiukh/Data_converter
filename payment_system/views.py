from django.core.mail import send_mail
from django.db.models import Prefetch
from rest_framework import generics, status
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from payment_system.permissions import ProjectPermission
from payment_system.models import (
    Project,
    UserProject,
    ProjectSubscription,
    Subscription,
    Invoice, Invitation,
)
from payment_system.serializers import (
    ProjectListSerializer,
    ProjectSerializer,
    ProjectSubscriptionSerializer,
    SubscriptionSerializer,
    InvoiceSerializer,
    ProjectInviteUserSerializer,
    InvitationListSerializer,
)
from users.models import DataOceanUser


class ProjectViewMixin:
    permission_classes = [IsAuthenticated, ProjectPermission]

    def get_queryset(self):
        return Project.objects.filter(
            users__in=[self.request.user],
            user_projects__status=UserProject.ACTIVE,
        ).prefetch_related(
            Prefetch('invitations', queryset=Invitation.objects.filter(deleted_at__isnull=True)),
            'subscriptions',
        )


class ProjectListForUserView(ProjectViewMixin, generics.ListAPIView):
    serializer_class = ProjectListSerializer

    def list(self, request, *args, **kwargs):
        projects = list(self.get_queryset())

        def sort_projects(project):
            rate = 2
            user_project = project.user_projects.get(user=self.request.user)
            if user_project.role == UserProject.OWNER:
                rate -= 1
            if project.is_active:
                rate -= 1
            return rate

        projects.sort(key=sort_projects)
        serializer = self.get_serializer(projects, many=True)
        return Response(serializer.data)


class ProjectRetrieveView(ProjectViewMixin, generics.RetrieveAPIView):
    serializer_class = ProjectSerializer


class ProjectCreateView(ProjectViewMixin, generics.CreateAPIView):
    serializer_class = ProjectSerializer


class ProjectUpdateView(ProjectViewMixin, generics.UpdateAPIView):
    serializer_class = ProjectSerializer


class ProjectDisableView(ProjectViewMixin, generics.GenericAPIView):
    serializer_class = ProjectSerializer

    def put(self, request, pk):
        project = self.get_object()

        # validation inside disable() method ->
        project.disable()

        serializer = self.get_serializer(project)
        return Response(serializer.data)


class ProjectActivateView(ProjectViewMixin, generics.GenericAPIView):
    serializer_class = ProjectSerializer

    def put(self, request, pk):
        project = self.get_object()

        project.activate()

        serializer = self.get_serializer(project)
        return Response(serializer.data)


class ProjectRefreshTokenView(ProjectViewMixin, generics.GenericAPIView):
    serializer_class = ProjectSerializer

    def put(self, request, pk):
        project = self.get_object()

        project.refresh_token()

        serializer = self.get_serializer(project)
        return Response(serializer.data)


class ProjectRemoveUserView(ProjectViewMixin, generics.GenericAPIView):
    serializer_class = ProjectSerializer

    def delete(self, request, pk, user_id):
        project = self.get_object()

        # validation inside remove_user() method ->
        project.remove_user(user_id=user_id)

        serializer = self.get_serializer(project)
        return Response(serializer.data)


class ProjectActivateUserView(ProjectViewMixin, generics.GenericAPIView):
    serializer_class = ProjectSerializer

    def put(self, request, pk, user_id):
        project = self.get_object()

        # validation inside activate_user() method ->
        project.activate_user(user_id=user_id)

        serializer = self.get_serializer(project)
        return Response(serializer.data)


class ProjectInviteUserView(ProjectViewMixin, generics.GenericAPIView):
    serializer_class = ProjectInviteUserSerializer

    def post(self, request, pk):
        project = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_email = serializer.validated_data['email']

        project.invite_user(user_email)

        serializer = ProjectSerializer(
            instance=project,
            context=self.get_serializer_context(),
        )
        return Response(serializer.data)


class ProjectCancelInviteView(ProjectViewMixin, generics.DestroyAPIView):
    serializer_class = ProjectSerializer

    def destroy(self, request, pk, invite_id):
        project = self.get_object()

        invitation = get_object_or_404(project.invitations, id=invite_id)
        invitation.soft_delete()

        serializer = self.get_serializer(project)
        return Response(serializer.data)


class ProjectUserConfirmInviteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        project.confirm_invitation(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProjectUserRejectInviteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        project.reject_invitation(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class InvitationListView(generics.ListAPIView):
    pagination_class = None
    serializer_class = InvitationListSerializer

    def get_queryset(self):
        return Invitation.objects.filter(
            email=self.request.user.email,
            deleted_at__isnull=True,
        )


class SubscriptionsListView(generics.ListAPIView):
    serializer_class = SubscriptionSerializer
    queryset = Subscription.objects.all()
    pagination_class = None


# TODO: permissions for user
class InvoiceRetrieveView(generics.RetrieveAPIView):
    queryset = Invoice
    serializer_class = InvoiceSerializer


# TODO: permissions for user
class InvoiceListView(generics.ListAPIView):
    queryset = Invoice
    serializer_class = InvoiceSerializer
    pagination_class = None


class ProjectSubscriptionCreateView(generics.CreateAPIView):
    serializer_class = ProjectSubscriptionSerializer
    queryset = ProjectSubscription.objects.all()


class ProjectSubscriptionDisableView(generics.GenericAPIView):
    serializer_class = ProjectSubscriptionSerializer
    queryset = ProjectSubscription.objects.all()

    def put(self, request, pk):
        project_subscription = self.get_object()

        project_subscription.disable()

        serializer = self.get_serializer(instance=project_subscription)
        return Response(serializer.data)
