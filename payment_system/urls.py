from django.urls import path
from payment_system.views import (
    ProjectCreateView,
    ProjectUpdateView,
    ProjectListForUserView,
    ProjectRetrieveView,
    ProjectRefreshTokenView,
    ProjectDisableView,
    ProjectActivateView,
    ProjectAddSubscriptionView,
    SubscriptionsListView,
    ProjectDeactivateUserView,
    ProjectActivateUserView,
    ProjectInviteUserView,
    ProjectUserConfirmInviteView,
    InvitationListView,
    ProjectCancelInviteView,
    ProjectUserRejectInviteView,
    CurrentUserProjectTokenView,
    UserInvoicesListView,
    SubscriptionInvoicesListView,
    ProjectSubscriptionRetrieveView,
    InvoicePDFView,
    ProjectRemoveSubscriptionView,
)

urlpatterns = [
    # project urls
    path('project/create/', ProjectCreateView.as_view()),

    path('project/<int:pk>/update/', ProjectUpdateView.as_view()),
    path('project/<int:pk>/refresh-token/', ProjectRefreshTokenView.as_view()),

    path('project/<int:pk>/disable/', ProjectDisableView.as_view()),
    path('project/<int:pk>/activate/', ProjectActivateView.as_view()),

    path('project/<int:pk>/deactivate-user/<int:user_id>/', ProjectDeactivateUserView.as_view()),
    path('project/<int:pk>/activate-user/<int:user_id>/', ProjectActivateUserView.as_view()),

    path('project/<int:pk>/invite/', ProjectInviteUserView.as_view()),
    path('project/<int:pk>/cancel-invite/<int:invite_id>/', ProjectCancelInviteView.as_view()),

    path('project/<int:pk>/confirm-invite/', ProjectUserConfirmInviteView.as_view()),
    path('project/<int:pk>/reject-invite/', ProjectUserRejectInviteView.as_view()),

    path('project/current/', CurrentUserProjectTokenView.as_view()),

    path('project/<int:pk>/', ProjectRetrieveView.as_view()),
    path('project/', ProjectListForUserView.as_view()),

    path('invitations/', InvitationListView.as_view()),

    path('subscriptions/', SubscriptionsListView.as_view()),

    path('invoice/<int:pk>/<uuid:token>/', InvoicePDFView.as_view(), name='invoice_pdf'),
    path('invoices/', UserInvoicesListView.as_view()),
    path('subscription/<int:pk>/invoices/', SubscriptionInvoicesListView.as_view()),

    path('project-subscription/<int:pk>/', ProjectSubscriptionRetrieveView.as_view()),

    path('project/<int:pk>/add-subscription/<int:subscription_id>/',
         ProjectAddSubscriptionView.as_view()),
    path('project/<int:pk>/remove-future-subscription/',
         ProjectRemoveSubscriptionView.as_view()),
]
