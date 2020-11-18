from rest_framework import generics
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from payment_system.permissions import ProjectPermission
from payment_system.serializers.project_serializers import (
    ProjectSerializer,
    ProjectListSerializer,
)
from payment_system.models import Project, UserProject


class ProjectViewMixin:
    permission_classes = [IsAuthenticated, ProjectPermission]

    def get_queryset(self):
        return Project.objects.filter(users__in=[self.request.user])


class ProjectListForUserView(ProjectViewMixin, generics.ListAPIView):
    serializer_class = ProjectListSerializer

    def list(self, request, *args, **kwargs):
        projects = list(self.get_queryset())

        def sort_projects(project):
            rate = 2
            user_project = project.user_projects.get(user=self.request.user)
            if user_project.role == UserProject.INITIATOR:
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
        project = get_object_or_404(self.get_queryset(), pk=pk)
        self.check_object_permissions(request, project)

        # validation inside disable() method ->
        project.disable()

        serializer = self.get_serializer(project)
        return Response(serializer.data)


class ProjectActivateView(ProjectViewMixin, generics.GenericAPIView):
    serializer_class = ProjectSerializer

    def put(self, request, pk):
        project = get_object_or_404(self.get_queryset(), pk=pk)
        self.check_object_permissions(request, project)

        project.activate()

        serializer = self.get_serializer(project)
        return Response(serializer.data)


class ProjectRefreshTokenView(ProjectViewMixin, generics.GenericAPIView):
    serializer_class = ProjectSerializer

    def put(self, request, pk):
        project = get_object_or_404(self.get_queryset(), pk=pk)
        self.check_object_permissions(request, project)
        project.refresh_token()
        serializer = self.get_serializer(project)
        return Response(serializer.data)
