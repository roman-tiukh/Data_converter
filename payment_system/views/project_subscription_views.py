from rest_framework import generics
from payment_system.serializers.project_subscription_serializers import ProjectSubscriptionSerializer
from payment_system.models import ProjectSubscription


class ProjectSubscriptionCreateView(generics.CreateAPIView):
    serializer_class = ProjectSubscriptionSerializer
    model = ProjectSubscription


class ProjectSubscriptionDisableView(generics.UpdateAPIView):
    serializer_class = ProjectSubscriptionSerializer
    model = ProjectSubscription
