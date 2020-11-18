from django.urls import path
from payment_system.views import (
    ProjectCreateView,
    ProjectUpdateView,
    ProjectListForUserView,
    ProjectRetrieveView,
    ProjectRefreshTokenView,
    ProjectDisableView,
    ProjectActivateView,
    ProjectSubscriptionCreateView,
    ProjectSubscriptionDisableView,
    SubscriptionsListView,
    ProjectRemoveUserView,
    ProjectActivateUserView,
    InvoiceListView,
    InvoiceRetrieveView,
    ProjectInviteUserView,
    ProjectUserConfirmInviteView,
    InvitationListView,
    ProjectCancelInviteView,
    ProjectUserRejectInviteView,
)

urlpatterns = [
    # project urls
    path('project/create/', ProjectCreateView.as_view()),

    path('project/<int:pk>/update/', ProjectUpdateView.as_view()),
    path('project/<int:pk>/refresh-token/', ProjectRefreshTokenView.as_view()),

    path('project/<int:pk>/disable/', ProjectDisableView.as_view()),
    path('project/<int:pk>/activate/', ProjectActivateView.as_view()),

    path('project/<int:pk>/remove-user/<int:user_id>/', ProjectRemoveUserView.as_view()),
    path('project/<int:pk>/activate-user/<int:user_id>/', ProjectActivateUserView.as_view()),

    path('project/<int:pk>/invite/', ProjectInviteUserView.as_view()),
    path('project/<int:pk>/cancel-invite/', ProjectCancelInviteView.as_view()),

    path('project/<int:pk>/confirm-invite/', ProjectUserConfirmInviteView.as_view()),
    path('project/<int:pk>/reject-invite/', ProjectUserRejectInviteView.as_view()),

    path('project/<int:pk>/', ProjectRetrieveView.as_view()),
    path('project/', ProjectListForUserView.as_view()),

    path('invitations/', InvitationListView.as_view()),

    path('subscriptions/', SubscriptionsListView.as_view()),

    path('invoice/<int:pk>/', InvoiceRetrieveView.as_view()),
    path('invoice/', InvoiceListView.as_view()),

    path('project-subscription/create/', ProjectSubscriptionCreateView.as_view()),
    path('project-subscription/<int:pk>/disable/', ProjectSubscriptionDisableView.as_view()),
]
