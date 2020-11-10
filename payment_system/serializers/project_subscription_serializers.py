from rest_framework import serializers
from payment_system.models import ProjectSubscription


class ProjectSubscriptionSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        return ProjectSubscription.create(**validated_data)

    class Meta:
        model = ProjectSubscription
        fields = ['id', 'project', 'subscription', 'status', 'expiring_date']
        read_only_fields = ['status', 'expiring_date']
