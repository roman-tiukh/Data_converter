from django.urls import path
from users import views
from users.views import (
    QuestionCreateView,
    NotificationListView,
    NotificationReadView,
    NotificationReadAllView,
    NotificationDeleteView,
)

urlpatterns = [
    path('', views.UserListView.as_view()),

    path('question/create/', QuestionCreateView.as_view()),

    path('notifications/<int:pk>/delete/', NotificationDeleteView.as_view()),
    path('notifications/<int:pk>/read/', NotificationReadView.as_view()),
    path('notifications/read-all/', NotificationReadAllView.as_view()),
    path('notifications/', NotificationListView.as_view()),
]
