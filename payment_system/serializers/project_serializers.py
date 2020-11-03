from rest_framework import serializers
from payment_system.models import Project


class ProjectSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        user = self.context['request'].user
        project = user.create_project(**validated_data)
        return project

    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'disabled_at', 'users', 'subscriptions']
        read_only_fields = ['disabled_at', 'users', 'subscriptions']
