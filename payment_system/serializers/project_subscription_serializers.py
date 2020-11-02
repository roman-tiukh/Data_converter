from rest_framework import serializers
from payment_system.models import ProjectSubscription


class ProjectSubscriptionSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        return ProjectSubscription.create(**validated_data)
    
    def update(self, validated_data):
        project_subscription = ProjectSubscription.disable(project, subscription)
        super(ProjectSubscriptionSerializer, self).update()


    class Meta:
        model = ProjectSubscription
        fields = ['project', 'subscription', 'status', 'expiring_date']
        read_only_fields = ['status', 'expiring_date']
