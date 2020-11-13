from rest_framework import serializers
from payment_system.models import (
    Project,
    ProjectSubscription,
    UserProject,
)


class SubscriptionToProjectSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='subscription.id')
    name = serializers.CharField(source='subscription.name')
    price = serializers.IntegerField(source='subscription.price')
    requests_limit = serializers.IntegerField(source='subscription.requests_limit')
    duration = serializers.IntegerField(source='subscription.duration')
    grace_period = serializers.IntegerField(source='subscription.duration')

    class Meta:
        model = ProjectSubscription
        fields = [
            'id', 'name', 'status', 'expiring_date',
            'price', 'requests_limit', 'duration', 'grace_period',
        ]
        read_only_fields = fields


class UserToProjectSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='user.id')
    name = serializers.CharField(source='user.get_full_name')
    email = serializers.EmailField(source='user.email')

    class Meta:
        model = UserProject
        fields = [
            'id', 'name', 'email', 'status', 'role',
        ]
        read_only_fields = fields


class ProjectListSerializer(serializers.ModelSerializer):
    is_default = serializers.SerializerMethodField(read_only=True)

    def get_is_default(self, obj):
        return obj.user_projects.get(user=self.context['request'].user).is_default

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'is_active', 'is_default',
        ]
        read_only_fields = fields


class ProjectSerializer(serializers.ModelSerializer):
    subscriptions = SubscriptionToProjectSerializer(source='project_subscriptions',
                                                    many=True, read_only=True)
    users = UserToProjectSerializer(source='user_projects',
                                    many=True, read_only=True)

    is_default = serializers.SerializerMethodField(read_only=True)

    def get_is_default(self, obj):
        return obj.user_projects.get(user=self.context['request'].user).is_default

    def create(self, validated_data):
        user = self.context['request'].user
        return Project.create(
            initiator=user,
            name=validated_data['name'],
            description=validated_data.get('description', '')
        )

    class Meta:
        model = Project
        read_only_fields = [
            'id', 'users', 'subscriptions', 'token', 'disabled_at',
            'is_active', 'is_default', 'is_default',
        ]
        fields = [
            'name', 'description',
        ] + read_only_fields
