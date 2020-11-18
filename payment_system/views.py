from django.core.mail import send_mail
from rest_framework import generics, status
from django.shortcuts import get_object_or_404
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
    Invoice,
)
from payment_system.serializers import (
    ProjectListSerializer,
    ProjectSerializer,
    ProjectSubscriptionSerializer,
    SubscriptionSerializer,
    InvoiceSerializer, ProjectInviteUserSerializer,
)
from users.models import DataOceanUser


class ProjectViewMixin:
    permission_classes = [IsAuthenticated, ProjectPermission]

    def get_queryset(self):
        return Project.objects.filter(
            users__in=[self.request.user],
            user_projects__status=UserProject.ACTIVE,
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

        # TODO: maybe send email for registration if not exists
        try:
            user = DataOceanUser.objects.get(email=user_email)
        except DataOceanUser.DoesNotExist:
            raise ValidationError({'detail': 'User does not exists'})

        project.invite_user(user)

        # TODO: send Email here
        print(f'Email sent to {user_email}')

        serializer = ProjectSerializer(
            instance=project,
            context=self.get_serializer_context(),
        )
        return Response(serializer.data)


class SubscriptionsListView(generics.ListAPIView):
    serializer_class = SubscriptionSerializer
    queryset = Subscription.objects.all()


# TODO: permissions for user
class InvoiceRetrieveView(generics.RetrieveAPIView):
    queryset = Invoice
    serializer_class = InvoiceSerializer


# TODO: permissions for user
class InvoiceListView(generics.ListAPIView):
    queryset = Invoice
    serializer_class = InvoiceSerializer


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
