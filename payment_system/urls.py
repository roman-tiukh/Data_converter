from django.urls import path
from payment_system.views.project_views import (
    ProjectCreateView,
    ProjectUpdateView,
    ProjectListForUserView,
    ProjectRetrieveView,
    ProjectRefreshTokenView,
    ProjectDisableView,
    ProjectActivateView,
)
from payment_system.views.project_subscription_views import (
    ProjectSubscriptionCreateView,
    ProjectSubscriptionDisableView,
)

urlpatterns = [
    path('project/create/', ProjectCreateView.as_view()),
    path('project/<int:pk>/update/', ProjectUpdateView.as_view()),
    path('project/<int:pk>/refresh-token/', ProjectRefreshTokenView.as_view()),
    path('project/<int:pk>/disable/', ProjectDisableView.as_view()),
    path('project/<int:pk>/activate/', ProjectActivateView.as_view()),
    path('project/<int:pk>/', ProjectRetrieveView.as_view()),
    path('project-subscription/create/', ProjectSubscriptionCreateView.as_view()),
    path('project-subscription/<int:pk>/disable/', ProjectSubscriptionDisableView.as_view()),
    path('project/', ProjectListForUserView.as_view()),
]
