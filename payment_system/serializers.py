from rest_framework import serializers
from payment_system.models import (
    Project,
    ProjectSubscription,
    UserProject,
    Subscription,
    Invoice,
    Invitation,
    CustomSubscriptionRequest,
)


# class ProjectSubscriptionSerializer(serializers.ModelSerializer):
#     def create(self, validated_data):
#         return ProjectSubscription.create(
#             project=validated_data['project'],
#             subscription=validated_data['subscription'],
#         )
#
#     class Meta:
#         model = ProjectSubscription
#         read_only_fields = ['status', 'expiring_date']
#         fields = [
#             'id', 'project', 'subscription'
#         ] + read_only_fields


class SubscriptionToProjectSerializer(serializers.ModelSerializer):
    subscription_id = serializers.IntegerField(source='subscription.id')
    name = serializers.CharField(source='subscription.name')
    price = serializers.IntegerField(source='subscription.price')
    requests_limit = serializers.IntegerField(source='subscription.requests_limit')
    is_default = serializers.BooleanField(source='subscription.is_default')

    class Meta:
        model = ProjectSubscription
        fields = [
            'id', 'subscription_id', 'name', 'status', 'expiring_date',
            'price', 'requests_limit', 'periodicity', 'grace_period',
            'requests_left', 'requests_used', 'is_paid',
            'payment_date', 'payment_overdue_days', 'is_default',
        ]
        read_only_fields = fields


class UserInProjectSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='user.id')
    name = serializers.CharField(source='user.get_full_name')
    email = serializers.EmailField(source='user.email')

    class Meta:
        model = UserProject
        fields = [
            'id', 'name', 'email', 'status', 'role', 'is_default',
        ]
        read_only_fields = fields


class ProjectListSerializer(serializers.ModelSerializer):
    is_default = serializers.SerializerMethodField(read_only=True)
    role = serializers.SerializerMethodField(read_only=True)
    status = serializers.SerializerMethodField(read_only=True)
    owner = serializers.CharField(source='owner.get_full_name', read_only=True)
    users_count = serializers.SerializerMethodField(read_only=True)

    active_subscription = SubscriptionToProjectSerializer(source='active_p2s', read_only=True)

    def get_is_default(self, obj):
        return obj.user_projects.get(user=self.context['request'].user).is_default

    def get_role(self, obj):
        return obj.user_projects.get(user=self.context['request'].user).role

    def get_status(self, obj):
        return obj.user_projects.get(user=self.context['request'].user).status

    def get_users_count(self, obj):
        return obj.users.filter(user_projects__status=UserProject.ACTIVE).count()


    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'is_active',
            'is_default', 'role', 'status', 'owner',
            'users_count', 'active_subscription', 'token',
        ]
        read_only_fields = fields


class ProjectInvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitation
        fields = ['id', 'email', 'updated_at']


class ProjectSerializer(serializers.ModelSerializer):
    subscriptions = SubscriptionToProjectSerializer(source='project_subscriptions',
                                                    many=True, read_only=True)
    users = UserInProjectSerializer(source='user_projects',
                                    many=True, read_only=True)
    is_default = serializers.SerializerMethodField(read_only=True)
    invitations = ProjectInvitationSerializer(many=True, read_only=True)

    owner = serializers.CharField(source='owner.get_full_name', read_only=True)
    is_owner = serializers.SerializerMethodField(read_only=True)

    def get_is_owner(self, obj):
        return obj.user_projects.get(user=self.context['request'].user).role == UserProject.OWNER

    def get_is_default(self, obj):
        return obj.user_projects.get(user=self.context['request'].user).is_default

    def create(self, validated_data):
        user = self.context['request'].user
        return Project.create(
            owner=user,
            name=validated_data['name'],
            description=validated_data.get('description', ''),

        )

    class Meta:
        model = Project
        read_only_fields = [
            'users', 'subscriptions', 'invitations', 'token',
            'is_active', 'is_default', 'disabled_at', 'owner',
            'created_at', 'is_owner',
        ]
        fields = [
            'id', 'name', 'description',
        ] + read_only_fields


class SubscriptionSerializer(serializers.ModelSerializer):
    pep_db_downloading_if_yearly = serializers.BooleanField(
        source='yearly_subscription.pep_db_downloading',
        default=False,
    )

    class Meta:
        model = Subscription
        read_only_fields = (
            'id', 'name', 'description', 'price',
            'requests_limit', 'platform_requests_limit', 'periodicity', 'grace_period',
            'is_custom', 'is_default', 'pep_checks', 'pep_checks_per_minute',
            'pep_db_downloading', 'position', 'yearly_subscription',
            'pep_db_downloading_if_yearly',
        )
        fields = read_only_fields


class InvoiceSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project_subscription.project.name')
    # subscription_name = serializers.CharField(source='project_subscription.subscription.name')

    class Meta:
        model = Invoice
        read_only_fields = (
            'id', 'token', 'paid_at', 'note', 'subscription_name',
            'project_name', 'price', 'is_paid',
        )
        fields = read_only_fields


class ProjectInviteUserSerializer(serializers.Serializer):
    email = serializers.EmailField()

    class Meta:
        fields = ['email']


class InvitationListSerializer(serializers.ModelSerializer):
    project_id = serializers.IntegerField(source='project.id', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    project_owner = serializers.CharField(source='project.owner.get_full_name', read_only=True)

    class Meta:
        model = Invitation
        fields = ['id', 'project_id', 'project_name', 'project_owner', 'updated_at']
        read_only_fields = fields


class ProjectTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['token']
        read_only_fields = fields


class ProjectShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'owner', 'disabled_at']
        read_only_fields = fields


class ProjectSubscriptionSerializer(serializers.ModelSerializer):
    project = ProjectShortSerializer()
    subscription = SubscriptionSerializer()

    class Meta:
        model = ProjectSubscription
        fields = [
            'id', 'project', 'subscription', 'status',
            'start_date', 'expiring_date', 'requests_left',
            'is_grace_period', 'periodicity', 'grace_period',
        ]
        read_only_fields = fields


class CustomSubscriptionRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomSubscriptionRequest
        read_only_fields = ['is_processed', 'created_at']
        fields = [
            'id', 'first_name', 'last_name',
            'email', 'phone', 'note',
        ] + read_only_fields
