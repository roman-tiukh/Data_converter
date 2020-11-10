from rest_framework import generics
from django.shortcuts import get_object_or_404
from payment_system.serializers.project_serializers import ProjectSerializer
from payment_system.models import Project


class ProjectCreateView(generics.CreateAPIView):
    serializer_class = ProjectSerializer
    model = Project


class ProjectUpdateView(generics.UpdateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    model = Project
