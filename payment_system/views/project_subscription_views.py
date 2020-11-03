from rest_framework import generics
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from payment_system.serializers.project_subscription_serializers import ProjectSubscriptionSerializer
from payment_system.models import ProjectSubscription


class ProjectSubscriptionCreateView(generics.CreateAPIView):
    serializer_class = ProjectSubscriptionSerializer
    model = ProjectSubscription


class ProjectSubscriptionDisableView(APIView):
    queryset = ProjectSubscription.objects.all()
    model = ProjectSubscription

    def put(self, request, pk):
        project_subscription = get_object_or_404(ProjectSubscription.objects.all(), pk=pk)
        project_subscription.disable()
        serializer = ProjectSubscriptionSerializer(instance=project_subscription)
        return Response(serializer.data, status=status.HTTP_200_OK)
