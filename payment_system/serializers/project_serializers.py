from rest_framework import serializers
from payment_system.models import Project


class ProjectCreateSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        user = self.context['request'].user
        project = user.create_project(validated_data['name'], validated_data['description'])
        return project

    class Meta:
        model = Project
        fields = ('name', 'description')
