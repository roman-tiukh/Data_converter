from rest_framework import generics
from payment_system.serializers.project_serializers import ProjectCreateSerializer
from payment_system.models import Project


class ProjectCreateView(generics.CreateAPIView):
    serializer_class = ProjectCreateSerializer
    model = Project
